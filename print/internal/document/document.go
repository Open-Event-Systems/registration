package document

import (
	"crypto/md5"
	"encoding/base64"
	"encoding/json"
	"io"
	cmdExec "os/exec"
	"print/internal/logic"

	"github.com/nikolalohinski/gonja/v2/config"
	"github.com/nikolalohinski/gonja/v2/exec"
	"github.com/nikolalohinski/gonja/v2/loaders"
)

type PrintConfig struct {
	Server      string           `yaml:"server"`
	Destination string           `yaml:"destination"`
	When        *logic.Condition `yaml:"when"`
}

type DocumentTypeConfig struct {
	Name         string                   `yaml:"name"`
	Template     string                   `yaml:"template"`
	Dependencies []logic.ValueOrEvaluable `yaml:"dependencies"`
	Print        []PrintConfig            `yaml:"print"`
	When         *logic.Condition         `yaml:"when"`
}

type DocumentType struct {
	Id           string
	Name         string
	tmplConfig   *config.Config
	env          *exec.Environment
	template     *exec.Template
	loader       loaders.Loader
	dependencies []logic.ValueOrEvaluable
	Print        []PrintConfig
	when         *logic.Condition
}

// Get a DocumentType struct from a config object
func (cfg *DocumentTypeConfig) GetDocumentType(tmplConfig *config.Config, loader loaders.Loader, env *exec.Environment, id string) (*DocumentType, error) {
	dt := &DocumentType{
		Id:           id,
		Name:         cfg.Name,
		tmplConfig:   tmplConfig,
		env:          env,
		loader:       loader,
		dependencies: cfg.Dependencies,
		Print:        cfg.Print,
		when:         cfg.When,
	}

	template, err := exec.NewTemplate(cfg.Template, tmplConfig, loader, env)
	if err != nil {
		return nil, err
	}
	dt.template = template

	return dt, nil
}

// Evaluate the when condition
func (t *DocumentType) EvaluateCondition(registration map[string]any) bool {
	if t.when == nil {
		return true
	}
	ctx := exec.NewContext(registration)
	res := t.when.EvaluateBool(ctx)
	return res
}

// Get the hash of the dependencies
func (t *DocumentType) GetHash(registration map[string]any) (string, error) {
	depStr, err := t.dependenciesStr(registration)
	if err != nil {
		return "", err
	}

	hash := md5.Sum([]byte(depStr))
	dst := make([]byte, base64.RawURLEncoding.EncodedLen(len(hash)))
	base64.RawURLEncoding.Encode(dst, hash[:])
	return string(dst)[:8], nil
}

// Render the template
func (t *DocumentType) Render(output io.Writer, registration map[string]any) error {
	jsonData, err := json.Marshal(registration)
	if err != nil {
		return err
	}

	ctx := t.env.Context.Inherit()
	ctx.Set("json", string(jsonData))

	err = t.template.Execute(output, ctx)
	if err != nil {
		return err
	}

	return nil
}

func (t *DocumentType) dependenciesStr(registration map[string]any) (string, error) {
	var strs []any
	ctx := exec.NewContext(registration)
	for _, expr := range t.dependencies {
		val := expr.Evaluate(ctx)
		strs = append(strs, val)
	}

	jsonStr, err := json.Marshal(strs)
	if err != nil {
		return "", err
	}
	return string(jsonStr), nil
}

// Evaluate the when condition
func (c *PrintConfig) EvaluateCondition(change map[string]any) bool {
	if c.When == nil {
		return false
	}
	ctx := exec.NewContext(change)
	res := c.When.EvaluateBool(ctx)
	return res
}

// Submit a print job
func (c *PrintConfig) Submit(filename string) error {
	cmd := cmdExec.Command(
		"lp",
		"-h",
		c.Server,
		"-d",
		c.Destination,
		"--",
		filename,
	)
	err := cmd.Run()
	if err != nil {
		return err
	}
	return nil
}
