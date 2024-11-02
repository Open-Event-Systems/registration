package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"print/internal/config"
	"print/internal/render"
	"print/internal/storage"

	"github.com/nikolalohinski/gonja/v2"
	"github.com/nikolalohinski/gonja/v2/loaders"
)

var ErrNotFound = errors.New("not found")

func makeMux(cfg *config.Config) *http.ServeMux {

	tmplConfig := gonja.DefaultConfig
	loader := loaders.MustNewFileSystemLoader(".")
	env := gonja.DefaultEnvironment

	eventDocTypes := cfg.LoadEventDocumentTypes(tmplConfig, loader, env)

	storageObj := storage.NewStorage(cfg.Storage)
	renderer := render.NewRenderer(cfg.ChromiumExec, 1)

	// Get a registration from the registration service
	getRegistration := func(eventId string, id string) (map[string]any, error) {
		res, err := http.Get(fmt.Sprintf("%s/events/%s/registrations/%s", cfg.RegistrationURL, eventId, id))
		if err != nil {
			return nil, err
		}
		defer res.Body.Close()
		if res.StatusCode != 200 {
			return nil, ErrNotFound
		}

		bodyData, err := io.ReadAll(res.Body)
		if err != nil {
			return nil, err
		}

		var data map[string]any
		err = json.Unmarshal(bodyData, &data)
		if err != nil {
			return nil, err
		}
		return data, nil
	}

	// Get a slice of available document types and their hashes
	listDocTypes := func(eventId string, registration map[string]any) ([][2]string, error) {
		types, ok := eventDocTypes[eventId]
		if !ok {
			return nil, ErrNotFound
		}

		var res [][2]string

		for tid, typ := range types {
			if typ.EvaluateCondition(registration) {
				hash, err := typ.GetHash(registration)
				if err != nil {
					return nil, err
				} else {
					res = append(res, [2]string{tid, hash})
				}
			}
		}
		return res, nil
	}

	// Render a document
	renderDoc := func(eventId string, id string, docType string, hash string, registration map[string]any) error {
		typ := config.GetDocumentType(eventDocTypes, eventId, docType)
		if typ == nil {
			return ErrNotFound
		}

		os.MkdirAll(storageObj.GetDocDir(eventId, id, docType), 0o755)
		tmpf, err := os.CreateTemp("", "render-*.html")
		if err != nil {
			return err
		}
		defer os.Remove(tmpf.Name())
		defer tmpf.Close()

		err = typ.Render(tmpf, registration)
		if err != nil {
			return err
		}
		tmpf.Close()

		err = renderer.Render(tmpf.Name(), storageObj.GetDocPath(eventId, id, docType, hash))
		return err
	}

	getFile := func(eventId string, id string, docType string, filename string) *os.File {
		path := filepath.Join(storageObj.GetDocDir(eventId, id, docType), filename)
		f, err := os.Open(path)
		if err != nil {
			return nil
		}
		return f
	}

	getOrRenderFile := func(eventId string, id string, docType string, filename string) (*os.File, error) {
		existingFile := getFile(eventId, id, docType, filename)
		if existingFile != nil {
			return existingFile, nil
		}

		registration, err := getRegistration(eventId, id)
		if err != nil {
			return nil, err
		}

		typ := config.GetDocumentType(eventDocTypes, eventId, docType)
		if typ == nil {
			return nil, ErrNotFound
		}

		if !typ.EvaluateCondition(registration) {
			return nil, ErrNotFound
		}

		hash, err := typ.GetHash(registration)
		if err != nil {
			return nil, err
		}

		hashFilename := fmt.Sprintf("%s.pdf", hash)
		if hashFilename != filename {
			return nil, ErrNotFound
		}

		err = renderDoc(eventId, id, docType, hash, registration)
		if err != nil {
			return nil, err
		}

		return os.Open(storageObj.GetDocPath(eventId, id, docType, hash))
	}

	mux := http.NewServeMux()

	mux.HandleFunc("/events/{event_id}/document-types", func(w http.ResponseWriter, req *http.Request) {
		if req.Method != "GET" {
			http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
			return
		}

		eventId := req.PathValue("event_id")
		types, ok := eventDocTypes[eventId]
		if !ok {
			http.NotFound(w, req)
			return
		}

		res := make(map[string]string)
		for tid, typ := range types {
			res[tid] = typ.Name
		}

		jsonData, err := json.Marshal(res)
		if err != nil {
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		w.Header().Add("Content-Type", "application/json")
		w.Header().Add("Content-Length", fmt.Sprintf("%d", len(jsonData)))
		w.WriteHeader(200)
		w.Write(jsonData)
	})

	mux.HandleFunc("/events/{event_id}/registrations/{id}/documents", func(w http.ResponseWriter, req *http.Request) {
		if req.Method != "GET" {
			http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
			return
		}

		eventId := req.PathValue("event_id")
		id := req.PathValue("id")
		registration, err := getRegistration(eventId, id)
		if err != nil {
			if errors.Is(err, ErrNotFound) {
				http.NotFound(w, req)
				return
			} else {
				log.Print(err)
				http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
				return
			}
		}

		types, err := listDocTypes(eventId, registration)
		if err != nil {
			if errors.Is(err, ErrNotFound) {
				http.NotFound(w, req)
				return
			} else {
				log.Print(err)
				http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
				return
			}
		}

		res := make(map[string]string)
		var scheme string = "http:"
		fwdProto := req.Header.Get("X-Forwarded-Proto")
		if fwdProto != "" {
			scheme = fwdProto + ":"
		}

		for _, entry := range types {
			res[entry[0]] = fmt.Sprintf("%s//%s/events/%s/registrations/%s/documents/%s/%s.pdf", scheme, req.Host, eventId, id, entry[0], entry[1])
		}
		jsonData, err := json.Marshal(res)
		if err != nil {
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		w.Header().Add("Content-Type", "application/json")
		w.Header().Add("Content-Length", fmt.Sprintf("%d", len(jsonData)))
		w.WriteHeader(200)
		w.Write(jsonData)
	})

	mux.HandleFunc("/events/{event_id}/registrations/{id}/documents/{type}/{filename}", func(w http.ResponseWriter, req *http.Request) {
		if req.Method != "GET" && req.Method != "HEAD" {
			http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
			return
		}

		eventId := req.PathValue("event_id")
		id := req.PathValue("id")
		docType := req.PathValue("type")
		filename := req.PathValue("filename")
		f, err := getOrRenderFile(eventId, id, docType, filename)
		if err != nil {
			if errors.Is(err, ErrNotFound) {
				http.NotFound(w, req)
				return
			} else {
				log.Print(err)
				http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
				return
			}
		}
		defer f.Close()
		data, _ := io.ReadAll(f)
		f.Close()

		w.Header().Add("Content-Type", "application/pdf")
		w.Header().Add("Content-Length", fmt.Sprintf("%d", len(data)))
		w.WriteHeader(200)

		if req.Method == "GET" {
			w.Write(data)
		}
	})

	return mux
}

func main() {
	if len(os.Args) != 2 {
		log.Fatalf("usage: %s <config file>", os.Args[0])
	}

	cfgFileName := os.Args[1]
	cfg := config.LoadConfig(cfgFileName)

	mux := makeMux(cfg)

	server := &http.Server{
		Addr:    "0.0.0.0:8000",
		Handler: mux,
	}

	log.Printf("print api listening on %s", server.Addr)
	server.ListenAndServe()
}
