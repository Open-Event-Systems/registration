package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"os"
	print "print/pkg"
)

func main() {
	if len(os.Args) != 3 {
		log.Fatalf("usage: %s <config file> <output file>", os.Args[0])
	}

	cfgFileName := os.Args[1]
	outputFileName := os.Args[2]

	cfg, err := print.LoadConfig(cfgFileName)
	if err != nil {
		panic(err)
	}

	templates, err := cfg.LoadTemplates()
	if err != nil {
		panic(err)
	}

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

	template := templates[eventId]
	if template == nil {
		panic(fmt.Errorf("no template for event: %s", eventId))
	}

	err = print.RenderPDF(cfg.ChromiumExec, template, outputFileName, dataObj)
	if err != nil {
		panic(err)
	}
}
