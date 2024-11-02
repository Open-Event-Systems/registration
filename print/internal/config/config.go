package config

import (
	"log"
	"os"
	"print/internal/document"

	"github.com/nikolalohinski/gonja/v2/config"
	"github.com/nikolalohinski/gonja/v2/exec"
	"github.com/nikolalohinski/gonja/v2/loaders"
	"gopkg.in/yaml.v3"
)

type EventConfig struct {
	DocumentTypes map[string]document.DocumentTypeConfig `yaml:"document_types"`
}

type Config struct {
	RegistrationURL string                 `yaml:"registration_url"`
	PrintURL        string                 `yaml:"print_url"`
	AMQPURL         string                 `yaml:"amqp_url"`
	Storage         string                 `yaml:"storage"`
	Events          map[string]EventConfig `yaml:"events"`
	ChromiumExec    string                 `yaml:"chromium-exec"`
}

// Load the config file
func LoadConfig(path string) *Config {
	data, err := os.ReadFile(path)
	if err != nil {
		panic(err)
	}
	var config *Config
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		panic(err)
	}
	return config
}

// Load document templates for each event
func (cfg *Config) LoadEventDocumentTypes(
	tmplConfig *config.Config,
	loader loaders.Loader,
	env *exec.Environment,
) map[string]map[string]*document.DocumentType {
	res := make(map[string]map[string]*document.DocumentType)
	for id, evtCfg := range cfg.Events {
		res[id] = evtCfg.LoadDocumentTypes(tmplConfig, loader, env)
	}
	return res
}

// Load the template files specified by the config file
func (cfg *EventConfig) LoadDocumentTypes(
	tmplConfig *config.Config,
	loader loaders.Loader,
	env *exec.Environment,
) map[string]*document.DocumentType {
	res := make(map[string]*document.DocumentType)

	for id, typ := range cfg.DocumentTypes {
		loaded, err := typ.GetDocumentType(tmplConfig, loader, env, id)
		if err != nil {
			log.Panicf("could not load document type %s: %v", id, err)
		}
		res[id] = loaded
	}

	return res
}

// Get a document type by event/type ID
func GetDocumentType(types map[string]map[string]*document.DocumentType, eventId string, docType string) *document.DocumentType {
	byType, ok := types[eventId]
	if !ok {
		return nil
	}

	return byType[docType]
}
