package pkg

import (
	"encoding/json"
	"io"
	"os"
	"os/exec"
	"text/template"
)

type renderData struct {
	JSON string
}

// Render a template, writing the result to destFileName
func RenderTemplate(tmpl *template.Template, destFileName string, data map[string]any) error {
	destFile, err := os.OpenFile(destFileName, os.O_RDWR, os.ModeAppend)
	if err != nil {
		return err
	}
	defer destFile.Close()

	jsonStr, err := json.Marshal(data)
	if err != nil {
		return err
	}

	err = tmpl.Execute(destFile, renderData{JSON: string(jsonStr)})
	if err != nil {
		return err
	}
	return nil
}

// Render a HTML page to a PDF file.
func HTMLToPDF(chromeExec string, inputFileName string, outputFileName string) error {
	tmpFile, err := os.CreateTemp("", "print*.pdf")
	if err != nil {
		return err
	}
	tmpFileName := tmpFile.Name()
	defer os.Remove(tmpFileName)
	defer tmpFile.Close()

	if chromeExec == "" {
		chromeExec = "chromium-browser"
	}

	cmd := exec.Command(
		chromeExec,
		"--headless=new",
		"--disable-gpu",
		"--no-sandbox",
		"--print-to-pdf="+tmpFileName,
		"--no-pdf-header-footer",
		inputFileName,
	)
	err = cmd.Run()
	if err != nil {
		return err
	}

	fileData, err := io.ReadAll(tmpFile)
	if err != nil {
		return err
	}
	err = os.WriteFile(outputFileName, fileData, 0o644)
	return err
}

// Render a template to a PDF
func RenderPDF(chromeExec string, tmpl *template.Template, outputFileName string, data map[string]any) error {
	tmplResultFile, err := os.CreateTemp("", "render*.html")
	if err != nil {
		return err
	}
	tmplResultFileName := tmplResultFile.Name()
	defer os.Remove(tmplResultFileName)
	defer tmplResultFile.Close()

	err = RenderTemplate(tmpl, tmplResultFileName, data)
	if err != nil {
		return err
	}

	err = HTMLToPDF(chromeExec, tmplResultFileName, outputFileName)
	return err
}
