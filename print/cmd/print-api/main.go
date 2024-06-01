package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	print "print/pkg"
)

func makeMux(config *print.Config) *http.ServeMux {

	templates, err := config.LoadTemplates()
	if err != nil {
		panic(err)
	}

	limitChan := make(chan struct{}, 1)

	printToPDF := func(w http.ResponseWriter, req *http.Request) {
		if req.Method != "POST" {
			http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
			return
		}

		body, err := io.ReadAll(req.Body)
		if err != nil {
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}

		jsonBody := make(map[string]any)
		err = json.Unmarshal(body, &jsonBody)
		if err != nil {
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}

		eventId, ok := jsonBody["event_id"].(string)
		if !ok {
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}

		template := templates[eventId]
		if template == nil {
			log.Printf("no template for event: %s", eventId)
			http.NotFound(w, req)
			return
		}

		tmpFile, err := os.CreateTemp("", "output*.pdf")
		if err != nil {
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			log.Print(err)
			return
		}
		tmpFileName := tmpFile.Name()
		defer os.Remove(tmpFileName)
		defer tmpFile.Close()

		limitChan <- struct{}{}
		err = print.RenderPDF(config.ChromiumExec, template, tmpFileName, jsonBody)
		<-limitChan

		if err != nil {
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			log.Print(err)
			return
		}

		outputData, err := io.ReadAll(tmpFile)
		if err != nil {
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			log.Print(err)
			return
		}

		w.Write(outputData)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/print-to-pdf", printToPDF)
	return mux
}

func main() {
	if len(os.Args) != 2 {
		log.Fatalf("usage: %s <config file>", os.Args[0])
	}

	cfgFileName := os.Args[1]
	cfg, err := print.LoadConfig(cfgFileName)
	if err != nil {
		panic(err)
	}

	mux := makeMux(cfg)

	server := &http.Server{
		Addr:    "0.0.0.0:8000",
		Handler: mux,
	}

	log.Printf("print api listening on %s", server.Addr)
	server.ListenAndServe()
}
