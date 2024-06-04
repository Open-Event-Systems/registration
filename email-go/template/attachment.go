package template

import (
	"fmt"
	"mime/multipart"
	"mime/quotedprintable"
	"net/textproto"
	"os"
	"path"

	"github.com/gabriel-vasile/mimetype"
)

const (
	AttachmentTypeInline     = "inline"
	AttachmentTypeAttachment = "attachment"
)

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

func (att *Attachment) MakeMIMEPart(multipartWriter *multipart.Writer) error {
	header := make(textproto.MIMEHeader)
	header.Set("Content-Type", att.MediaType)
	header.Set("Content-Disposition", formatContentDisp(att.AttachmentType, att.Name))
	header.Set("Content-ID", fmt.Sprintf("<%s>", att.Id))
	header.Set("Content-Transfer-Encoding", "quoted-printable")
	partWriter, err := multipartWriter.CreatePart(header)
	if err != nil {
		return err
	}

	qpPartWriter := quotedprintable.NewWriter(partWriter)

	_, err = qpPartWriter.Write(att.Data)
	if err != nil {
		return err
	}

	qpPartWriter.Close()
	return nil
}

func formatContentDisp(disp string, filename string) string {
	return fmt.Sprintf("%s; filename=\"%s\"", disp, filename)
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
