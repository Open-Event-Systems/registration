package pkg

import (
	"fmt"
	"os"
	"path/filepath"
)

// Ensure the directory to store a registration document exists.
func EnsureStoragePathExists(basePath string, eventId string, id string) error {
	return os.MkdirAll(getRegPath(basePath, eventId, id), 0o0755)
}

// Get the file path for a registration document.
func GetFilePath(basePath string, eventId string, id string, version int) string {
	filename := fmt.Sprintf("%d.pdf", version)
	return filepath.Join(getRegPath(basePath, eventId, id), filename)
}

func getRegPath(basePath string, eventId string, id string) string {
	return filepath.Join(basePath, eventId, id[0:1], id[1:2], id)
}
