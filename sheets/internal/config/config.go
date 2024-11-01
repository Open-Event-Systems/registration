package config

import (
	"os"
	"sheets_hook/internal/template"

	"gopkg.in/yaml.v3"
)

type Config struct {
	AMQPURL         string  `yaml:"amqp_url"`
	CredentialsFile string  `yaml:"credentials_file"`
	SpreadsheetId   string  `yaml:"spreadsheet_id"`
	Range           string  `yaml:"range"`
	Columns         Columns `yaml:"columns"`
}

type Columns struct {
	TemplateConfig *template.TemplateConfig
	Expressions    []*template.Expression
}

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

func (c *Columns) UnmarshalYAML(unmarshal func(interface{}) error) error {
	var exprStrs []string
	err := unmarshal(&exprStrs)
	if err != nil {
		return err
	}

	tmplCfg := template.NewTemplateConfig()
	var exprs []*template.Expression

	for _, src := range exprStrs {
		expr, err := tmplCfg.ParseExpression(src)
		if err != nil {
			return err
		}

		exprs = append(exprs, expr)
	}

	c.TemplateConfig = tmplCfg
	c.Expressions = exprs
	return nil
}

func (c *Columns) EvaluateColumns(data map[string]any) []any {
	var results []any
	for _, expr := range c.Expressions {
		res := expr.Evaluate(data)
		results = append(results, res)
	}
	return results
}
