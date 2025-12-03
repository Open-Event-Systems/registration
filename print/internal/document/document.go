package document

import (
	"bytes"
	"crypto/md5"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"print/internal/logic"

	"github.com/OpenPrinting/goipp"
	"github.com/nikolalohinski/gonja/v2/config"
	"github.com/nikolalohinski/gonja/v2/exec"
	"github.com/nikolalohinski/gonja/v2/loaders"
)

type PrintConfig struct {
	URL      string           `yaml:"url"`
	Username string           `yaml:"username"`
	Password string           `yaml:"password"`
	When     *logic.Condition `yaml:"when"`
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
	f, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer f.Close()
	err = submitFile(c.URL, c.Username, c.Password, f)
	return err
}

func submitFile(printerURL string, username string, password string, file io.Reader) error {
	req := goipp.NewRequest(goipp.DefaultVersion, goipp.OpPrintJob, 1)

	// https://datatracker.ietf.org/doc/html/rfc8011#section-4.2.1.1
	req.Operation.Add(goipp.MakeAttr("attributes-charset", goipp.TagCharset, goipp.String("utf-8")))
	req.Operation.Add(goipp.MakeAttr("attributes-natural-language", goipp.TagLanguage, goipp.String("en")))
	req.Operation.Add(goipp.MakeAttr("printer-uri", goipp.TagURI, goipp.String(printerURL)))

	if username != "" {
		req.Operation.Add(goipp.MakeAttr("requesting-user-name", goipp.TagName, goipp.String(username)))
	}

	req.Operation.Add(goipp.MakeAttr("document-format", goipp.TagMimeType, goipp.String("application/pdf")))

	ippData, err := req.EncodeBytes()
	if err != nil {
		return err
	}

	body := io.MultiReader(bytes.NewBuffer(ippData), file)

	httpReq, err := http.NewRequest("POST", printerURL, body)
	if err != nil {
		return err
	}

	httpReq.Header.Set("content-type", goipp.ContentType)
	httpReq.Header.Set("accept", goipp.ContentType)

	if username != "" {
		httpReq.SetBasicAuth(username, password)
	}

	resp, err := http.DefaultClient.Do(httpReq)
	if resp != nil {
		defer resp.Body.Close()
	}

	if err != nil {
		return err
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	var ippResp goipp.Message
	err = ippResp.Decode(resp.Body)
	if err != nil {
		return err
	}

	if goipp.Status(ippResp.Code) != goipp.StatusOk {
		return fmt.Errorf("unexpected IPP status: %d %s", ippResp.Code, goipp.Status(ippResp.Code))
	}

	return nil
}
