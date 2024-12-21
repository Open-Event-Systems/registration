package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"os"
	"print/internal/config"
	"print/internal/render"

	"github.com/nikolalohinski/gonja/v2"
	"github.com/nikolalohinski/gonja/v2/loaders"
)

func main() {
	if len(os.Args) != 4 {
		log.Fatalf("usage: %s <config file> <document type> <output file>", os.Args[0])
	}

	cfgFileName := os.Args[1]
	docType := os.Args[2]
	outputFileName := os.Args[3]

	cfg := config.LoadConfig(cfgFileName)

	tmplCfg := gonja.DefaultConfig
	loader := loaders.MustNewFileSystemLoader(".")
	env := gonja.DefaultEnvironment

	eventDocTypes := cfg.LoadEventDocumentTypes(tmplCfg, loader, env)

	renderer := render.NewRenderer(cfg.ChromiumExec, 1)

	data, err := io.ReadAll(os.Stdin)
	if err != nil {
		panic(err)
	}

	dataObj := make(map[string]any)
	err = json.Unmarshal(data, &dataObj)
	if err != nil {
		panic(err)
	}

	eventId, ok := dataObj["event_id"].(string)
	if !ok {
		panic(errors.New("invalid event_id"))
	}

	docTypeObj := config.GetDocumentType(eventDocTypes, eventId, docType)
	if docTypeObj == nil {
		panic(fmt.Errorf("invalid event/type: %s/%s", eventId, docType))
	}

	tmpf, err := os.CreateTemp("", "render-*.html")
	if err != nil {
		panic(err)
	}
	defer os.Remove(tmpf.Name())
	defer tmpf.Close()

	err = docTypeObj.Render(tmpf, dataObj)
	if err != nil {
		panic(err)
	}
	tmpf.Close()

	err = renderer.Render(tmpf.Name(), outputFileName)
	if err != nil {
		panic(err)
	}
}
