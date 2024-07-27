package template

import (
	"bytes"
	"email/config"
	"fmt"

	"github.com/nikolalohinski/gonja/v2"
	gonjaConfig "github.com/nikolalohinski/gonja/v2/config"
	"github.com/nikolalohinski/gonja/v2/exec"
	"github.com/nikolalohinski/gonja/v2/loaders"
	"github.com/tdewolff/minify/v2"
	"github.com/tdewolff/minify/v2/html"
	"github.com/vanng822/go-premailer/premailer"
)

type TemplateEnvironment struct {
	env         *exec.Environment
	baseDir     string
	loader      loaders.Loader
	gonjaConfig *gonjaConfig.Config
}

type TemplateInput struct {
	To       string
	From     string
	SMTPFrom string
	Subject  string
	Data     map[string]interface{}
}

type TemplateResult struct {
	Text        string
	HTML        string
	Attachments *Attachments
	context     *exec.Context
}

func NewEnvironment(config *config.Config) *TemplateEnvironment {
	return &TemplateEnvironment{
		env:         gonja.DefaultEnvironment,
		baseDir:     config.TemplatePath,
		gonjaConfig: gonja.DefaultConfig,
		loader:      loaders.MustNewFileSystemLoader(config.TemplatePath),
	}
}

func (env *TemplateEnvironment) Render(name string, input *TemplateInput) *TemplateResult {
	attachments := &Attachments{}

	emailData := map[string]interface{}{
		"to":      input.To,
		"from":    input.From,
		"smtp_from": input.SMTPFrom,
		"subject": input.Subject,
	}
	ctx := exec.NewContext(input.Data)
	ctx.Set("email", emailData)
	ctx.Set("inline", attachments.GetInlineFunc(env.baseDir))
	ctx.Set("attach", attachments.GetAttachFunc(env.baseDir))

	strRes := env.renderText(name, ctx)
	htmlRes := env.renderHTML(name, ctx)
	return &TemplateResult{
		Text:        strRes,
		HTML:        htmlRes,
		Attachments: attachments,
		context:     ctx,
	}
}

func (env *TemplateEnvironment) renderText(name string, context *exec.Context) string {
	tmplName := fmt.Sprintf("%s.txt", name)
	tmpl, err := exec.NewTemplate(tmplName, env.gonjaConfig, env.loader, env.env)
	if err != nil {
		panic(err)
	}

	res, err := tmpl.ExecuteToString(context)
	if err != nil {
		panic(err)
	}
	return res
}

func (env *TemplateEnvironment) renderHTML(name string, context *exec.Context) string {
	tmplName := fmt.Sprintf("%s.html", name)
	tmpl, err := exec.NewTemplate(tmplName, env.gonjaConfig, env.loader, env.env)
	if err != nil {
		return ""
	}

	res, err := tmpl.ExecuteToString(context)
	if err != nil {
		panic(err)
	}
	return processHTML(res)
}

func processHTML(htmlStr string) string {
	opts := premailer.NewOptions()
	opts.RemoveClasses = true
	prem, err := premailer.NewPremailerFromString(htmlStr, opts)
	if err != nil {
		panic(err)
	}

	res, err := prem.Transform()
	if err != nil {
		panic(err)
	}

	m := minify.New()
	htmlMinifier := &html.Minifier{
		KeepComments:        false,
		KeepSpecialComments: false,
		KeepDefaultAttrVals: true,
		KeepDocumentTags:    true,
		KeepEndTags:         true,
		KeepQuotes:          true,
		KeepWhitespace:      false,
	}
	m.AddFunc("text/html", htmlMinifier.Minify)

	inBuf := bytes.NewBufferString(res)
	outBuf := bytes.NewBufferString("")
	err = m.Minify("text/html", outBuf, inBuf)
	if err != nil {
		panic(err)
	}

	return outBuf.String()
}
