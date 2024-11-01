package template

import (
	"encoding/base64"
	"fmt"
	"io"
	"mime/multipart"
	"net/textproto"
	"os"
	"path"

	"github.com/gabriel-vasile/mimetype"
)

const (
	AttachmentTypeInline     = "inline"
	AttachmentTypeAttachment = "attachment"
)

const MAX_LINE_LENGTH = 72

type Attachment struct {
	Id             string
	Name           string
	Data           []byte
	MediaType      string
	AttachmentType string
}

type Attachments struct {
	curId       int
	Attachments []Attachment
}

type wrapWriter struct {
	writer io.Writer
	curLen int
}

func (att *Attachment) MakeMIMEPart(multipartWriter *multipart.Writer) error {
	header := make(textproto.MIMEHeader)
	header.Set("Content-Type", att.MediaType)
	header.Set("Content-Disposition", formatContentDisp(att.AttachmentType, att.Name))
	header.Set("Content-ID", fmt.Sprintf("<%s>", att.Id))
	header.Set("Content-Transfer-Encoding", "base64")
	partWriter, err := multipartWriter.CreatePart(header)
	if err != nil {
		return err
	}

	// line wrap the base64 encoded data
	// some mail servers do not handle very long lines
	wrap := &wrapWriter{partWriter, 0}
	base64PartWriter := base64.NewEncoder(base64.StdEncoding, wrap)

	_, err = base64PartWriter.Write(att.Data)
	if err != nil {
		return err
	}

	base64PartWriter.Close()
	return nil
}

func formatContentDisp(disp string, filename string) string {
	return fmt.Sprintf("%s; filename=\"%s\"", disp, filename)
}

func (w *wrapWriter) Write(data []byte) (int, error) {
	dataIdx := 0
	for dataIdx < len(data) {
		avail := MAX_LINE_LENGTH - w.curLen
		if avail == 0 {
			_, err := w.writer.Write([]byte("\r\n"))
			if err != nil {
				return 0, err
			}
			w.curLen = 0
			avail = MAX_LINE_LENGTH
		}

		left := len(data) - dataIdx
		toWrite := min(avail, left)
		_, err := w.writer.Write(data[dataIdx:dataIdx+toWrite])
		if err != nil {
			return 0, err
		}
		dataIdx += toWrite
		w.curLen += toWrite
	}
	return len(data), nil
}


func (a *Attachments) AddAttachment(attachmentType string, baseDir string, filename string) (string, error) {
	basename := path.Base(filename)
	fullPath := path.Join(baseDir, filename)
	fileData, err := os.ReadFile(fullPath)
	if err != nil {
		return "", err
	}

	mimeType := mimetype.Detect(fileData)

	a.curId += 1
	id := a.curId
	idStr := fmt.Sprintf("%d", id)

	a.Attachments = append(a.Attachments, Attachment{
		Id:             idStr,
		Name:           basename,
		Data:           fileData,
		MediaType:      mimeType.String(),
		AttachmentType: attachmentType,
	})
	return idStr, nil
}

func (a *Attachments) GetAttachFunc(baseDir string) func(filename string) string {
	return func(filename string) string {
		attId, err := a.AddAttachment(AttachmentTypeAttachment, baseDir, filename)
		if err != nil {
			panic(err)
		}
		return attId
	}
}

func (a *Attachments) GetInlineFunc(baseDir string) func(filename string) string {
	return func(filename string) string {
		attId, err := a.AddAttachment(AttachmentTypeInline, baseDir, filename)
		if err != nil {
			panic(err)
		}
		return attId
	}
}
