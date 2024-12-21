package storage

import (
	"fmt"
	"os"
	"path/filepath"
)

type Storage struct {
	root string
}

func NewStorage(root string) *Storage {
	os.MkdirAll(root, 0o755)
	return &Storage{root}
}

// Get the path to a document
func (s *Storage) GetDocPath(eventId string, id string, docType string, hash string) string {
	fn := fmt.Sprintf("%s.pdf", hash)
	return filepath.Join(s.GetDocDir(eventId, id, docType), fn)
}

// Get the directory a document is stored in
func (s *Storage) GetDocDir(eventId string, id string, docType string) string {
	return filepath.Join(s.root, eventId, id[0:1], id[1:2], id, docType)
}
