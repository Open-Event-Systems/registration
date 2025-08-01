package config

import (
	"os"

	"github.com/Open-Event-Systems/gonjaexpr/logic"
	"github.com/Open-Event-Systems/gonjaexpr/parse"
	"github.com/nikolalohinski/gonja/v2"
	"github.com/nikolalohinski/gonja/v2/exec"
	"gopkg.in/yaml.v3"
)

type Condition struct {
	eval logic.Evaluable
}

func (c *Condition) Evaluate(context *exec.Context) (any, error) {
	return c.eval.Evaluate(context)
}

func (c *Condition) UnmarshalYAML(unmarshal func(value any) error) error {

	var value any
	err := unmarshal(&value)
	if err != nil {
		return err
	}

	eval := exec.Evaluator{
		Config:      gonja.DefaultConfig,
		Environment: gonja.DefaultEnvironment,
		Loader:      gonja.DefaultLoader,
	}

	cond, err := parse.ParseCondition(eval, value)
	if err != nil {
		return err
	}

	c.eval = cond
	return nil
}

type Expression struct {
	eval logic.Evaluable
}

func (e *Expression) Evaluate(context *exec.Context) (any, error) {
	return e.eval.Evaluate(context)
}

func (e *Expression) UnmarshalYAML(unmarshal func(value any) error) error {

	var value any
	err := unmarshal(&value)
	if err != nil {
		return err
	}

	eval := exec.Evaluator{
		Config:      gonja.DefaultConfig,
		Environment: gonja.DefaultEnvironment,
		Loader:      gonja.DefaultLoader,
	}

	cond, err := parse.ParseCondition(eval, value)
	if err != nil {
		return err
	}

	e.eval = cond
	return nil
}

type ModifierConfig struct {
	Id     string    `yaml:"id"`
	Name   string    `yaml:"name,omitempty"`
	Amount int       `yaml:"amount"`
	When   Condition `yaml:"when"`
}

type LineItemConfig struct {
	Id          string           `yaml:"id,omitempty"`
	Name        string           `yaml:"name"`
	Description string           `yaml:"description,omitempty"`
	Price       int              `yaml:"price"`
	Modifiers   []ModifierConfig `yaml:"modifiers,omitempty"`
	When        Condition        `yaml:"when"`
}

type EventConfig struct {
	ScriptDir   string           `yaml:"script_dir"`
	DisplayName Expression  `yaml:"display_name"`
	LineItems   []LineItemConfig `yaml:"line_items"`
}

type Config struct {
	Events map[string]EventConfig `yaml:"events"`
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
