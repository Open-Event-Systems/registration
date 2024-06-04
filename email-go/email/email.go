package email

import (
	"email/template"
)

type Email struct {
	From        string
	To          string
	Subject     string
	Attachments []template.Attachment
	Text        string
	HTML        string
}

type Sender interface {
	Send(email *Email) error
}
