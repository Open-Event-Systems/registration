package pricing

import (
	"encoding/json"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"pricing/internal/structs"
)

func GetPricingScripts(dir string) []PricingFunc {
	scripts := getScripts(dir)
	var funcs []PricingFunc
	for _, script := range scripts {
		funcs = append(funcs, getScriptFunc(script))
	}
	return funcs
}

func getScripts(dir string) []string {
	var results []string
	entries, _ := os.ReadDir(dir)
	for _, file := range entries {
		info, err := file.Info()
		if err == nil && !info.IsDir() && info.Mode().Perm()&0o111 > 0 {
			results = append(results, filepath.Join(dir, file.Name()))
		}
	}
	return results
}

func getScriptFunc(file string) PricingFunc {
	return func(req *structs.PricingRequest) (*structs.PricingResult, error) {
		jsonData, err := json.Marshal(req)
		if err != nil {
			return nil, err
		}

		cmd := exec.Command(file)
		stdin, err := cmd.StdinPipe()
		if err != nil {
			return nil, err
		}

		stdout, err := cmd.StdoutPipe()
		if err != nil {
			return nil, err
		}

		stderr, err := cmd.StderrPipe()
		if err != nil {
			return nil, err
		}


		err = cmd.Start()
		if err != nil {
			return nil, err
		}
		defer cmd.Wait()
		stdin.Write(jsonData)
		stdin.Close()

		data, _ := io.ReadAll(stderr)
		log.Printf("%v", string(data))
		log.Printf("%v", string(jsonData))

		var result structs.PricingResult
		err = json.NewDecoder(stdout).Decode(&result)
		if err != nil {
			return nil, err
		}

		cmd.Wait()
		return &result, nil
	}
}
