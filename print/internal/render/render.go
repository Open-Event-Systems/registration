package render

import (
	"os"
	"os/exec"
	"path/filepath"
)

type Renderer struct {
	chromeExec string
	sem        chan struct{}
}

func NewRenderer(chromeExec string, maxConcurrent int) *Renderer {
	return &Renderer{
		chromeExec: chromeExec,
		sem:        make(chan struct{}, maxConcurrent),
	}
}

// Render a file as a PDF
func (r *Renderer) Render(inputFileName string, outputFileName string) error {
	r.acquire()
	defer r.release()
	outDir := filepath.Dir(outputFileName)
	tmpFile, err := os.CreateTemp(outDir, ".output-*.pdf")
	if err != nil {
		return err
	}
	defer os.Remove(tmpFile.Name())
	tmpFile.Close()

	execStr := r.chromeExec
	if execStr == "" {
		execStr = "chromium-browser"
	}

	cmd := exec.Command(
		execStr,
		"--headless=new",
		"--disable-gpu",
		"--no-sandbox",
		"--print-to-pdf="+tmpFile.Name(),
		"--no-pdf-header-footer",
		inputFileName,
	)
	err = cmd.Run()
	if err != nil {
		return err
	}

	err = os.Rename(tmpFile.Name(), outputFileName)

	return err
}

func (r *Renderer) acquire() {
	r.sem <- struct{}{}
}

func (r *Renderer) release() {
	<-r.sem
}
