package config

import (
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	TemplatePath string                   `yaml:"template_path"`
	From         string                   `yaml:"email_from"`
	Use          string                   `yaml:"use"`
	SMTPConfig   SMTPConfig               `yaml:"smtp"`
	Messages     map[string]MessageConfig `yaml:"messages"`
}

type SMTPConfig struct {
	Server   string  `yaml:"server"`
	Port     int     `yaml:"port"`
	Username *string `yaml:"username"`
	Password string `yaml:"password"`
	TLS      string `yaml:"tls"`
}

type MessageConfig struct {
	From    string `yaml:"email_from"`
	Subject string `yaml:"subject"`
}

func LoadConfig(configFile string) *Config {
	fileData, err := os.ReadFile(configFile)
	if err != nil {
		panic(err)
	}
	var config *Config
	err = yaml.Unmarshal(fileData, &config)
	if err != nil {
		panic(err)
	}

	return config
}
