package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	print "print/pkg"
	"strconv"
)

func makeMux(config *print.Config) *http.ServeMux {

	templates, err := config.LoadTemplates()
	if err != nil {
		panic(err)
	}

	limitChan := make(chan struct{}, 1)

	createFile := func(eventId string, id string, version int, data map[string]any) (*os.File, error) {
		template := templates[eventId]
		if template == nil {
			return nil, fmt.Errorf("no template for event: %s", eventId)
		}

		outputFileName := print.GetFilePath(config.Storage, eventId, id, version)
		err := print.EnsureStoragePathExists(config.Storage, eventId, id)
		if err != nil {
			return nil, err
		}

		limitChan <- struct{}{}
		err = print.RenderPDF(config.ChromiumExec, template, outputFileName, data)
		<-limitChan
		if err != nil {
			return nil, err
		}

		return os.Open(outputFileName)
	}

	getPDF := func(w http.ResponseWriter, req *http.Request) {
		eventId := req.PathValue("event_id")
		id := req.PathValue("id")
		versionStr := req.URL.Query().Get("version")

		if len(id) < 2 {
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}

		version, err := strconv.ParseInt(versionStr, 10, 32)
		if err != nil {
			version = 1
		}

		fileName := print.GetFilePath(config.Storage, eventId, id, int(version))
		file, err := os.Open(fileName)
		if err != nil {
			http.NotFound(w, req)
			return
		}

		data, err := io.ReadAll(file)
		if err != nil {
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			log.Printf("error reading %s: %s", fileName, err)
			return
		}

		w.Write(data)
	}

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

		eventId, eventIdOk := jsonBody["event_id"].(string)
		versionFloat, verOk := jsonBody["version"].(float64)
		id, idOk := jsonBody["id"].(string)

		if !eventIdOk || !idOk || len(id) < 2 {
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}

		var version int

		if !verOk {
			version = 1
		} else {
			version = int(versionFloat)
		}

		outputFile, err := createFile(eventId, id, version, jsonBody)

		if err != nil {
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			log.Print(err)
			return
		}
		defer outputFile.Close()

		outputData, err := io.ReadAll(outputFile)
		if err != nil {
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			log.Print(err)
			return
		}

		w.Write(outputData)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/events/{event_id}/registrations/{id}/badge", getPDF)
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
