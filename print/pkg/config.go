package pkg

import (
	"os"
	"path/filepath"
	"text/template"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Templates    map[string]string `yaml:"templates"`
	ChromiumExec string            `yaml:"chromium-exec"`
}

// Load the config file.
func LoadConfig(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var config *Config
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		return nil, err
	}
	return config, nil
}

// Load the template files specified by the config file.
func (cfg *Config) LoadTemplates() (map[string]*template.Template, error) {
	templates := make(map[string]*template.Template)

	for eventId, tmplPath := range cfg.Templates {
		tmpl, err := loadTemplate(tmplPath)
		if err != nil {
			return nil, err
		}
		templates[eventId] = tmpl
	}

	return templates, nil
}

func loadTemplate(filePath string) (*template.Template, error) {
	baseName := filepath.Base(filePath)
	tmpl, err := template.New(baseName).ParseFiles(filePath)
	return tmpl, err
}
