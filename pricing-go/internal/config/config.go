package config

import (
	"os"
	"pricing/internal/logic"

	"gopkg.in/yaml.v3"
)

type ModifierConfig struct {
	Id     string          `yaml:"id"`
	Name   string          `yaml:"name,omitempty"`
	Amount int             `yaml:"amount"`
	When   logic.Condition `yaml:"when"`
}

type LineItemConfig struct {
	Id          string           `yaml:"id,omitempty"`
	Name        string           `yaml:"name"`
	Description string           `yaml:"description,omitempty"`
	Price       int              `yaml:"price"`
	Modifiers   []ModifierConfig `yaml:"modifiers,omitempty"`
	When        logic.Condition  `yaml:"when"`
}

type Config struct {
	ScriptDir   string           `yaml:"script_dir"`
	DisplayName logic.Expression `yaml:"display_name"`
	LineItems   []LineItemConfig `yaml:"line_items"`
}

func LoadConfig(filename string) *Config {
	data, err := os.ReadFile(filename)
	if err != nil {
		panic(err)
	}

	var config Config
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		panic(err)
	}
	return &config
}
