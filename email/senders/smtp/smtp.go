package smtp

import (
	"bytes"
	"email/config"
	"email/email"
	"email/template"
	"fmt"
	"mime/multipart"
	"mime/quotedprintable"
	"net/textproto"

	"github.com/emersion/go-sasl"
	"github.com/emersion/go-smtp"
)

type smtpSender struct {
	config *config.SMTPConfig
}

func NewSMTPSender(config *config.SMTPConfig) email.Sender {
	return &smtpSender{config: config}
}

func (s *smtpSender) Send(email *email.Email) error {
	var err error
	var client *smtp.Client

	serverPort := fmt.Sprintf("%s:%d", s.config.Server, s.config.Port)

	switch s.config.TLS {
	case "ssl":
		client, err = smtp.DialTLS(serverPort, nil)
	case "starttls":
		client, err = smtp.DialStartTLS(serverPort, nil)
	default:
		client, err = smtp.Dial(serverPort)
	}

	if err != nil {
		return err
	}

	if s.config.Username != nil {
		saslClient := sasl.NewPlainClient("", *s.config.Username, s.config.Password)
		err = client.Auth(saslClient)
		if err != nil {
			return err
		}
	}

	var smtpfrom string

	if email.SMTPFrom != "" {
		smtpfrom = email.SMTPFrom
	} else {
		smtpfrom = email.From
	}

	msg := createMessage(email)
	msgReader := bytes.NewBuffer(msg)
	err = client.SendMail(smtpfrom, []string{email.To}, msgReader)
	if err != nil {
		return err
	}
	return nil
}

func createMessage(email *email.Email) []byte {
	buf := bytes.Buffer{}
	writer := multipart.NewWriter(&buf)

	var msgfrom string

	if email.From != "" {
		msgfrom = email.From
	} else {
		msgfrom = email.SMTPFrom
	}

	buf.WriteString(fmt.Sprintf("From: %s\r\n", msgfrom))
	buf.WriteString(fmt.Sprintf("To: %s\r\n", email.To))
	if email.Subject != "" {
		buf.WriteString(fmt.Sprintf("Subject: %s\r\n", email.Subject))
	}

	buf.WriteString(fmt.Sprintf("Content-Type: multipart/mixed; boundary=%s\r\n", writer.Boundary()))

	buf.WriteString("\r\n")

	if email.HTML != "" {
		altPartHeaders, altPartData := createAlternativePart(email)
		altPart, err := writer.CreatePart(altPartHeaders)
		if err != nil {
			panic(err)
		}
		altPart.Write(altPartData)
	} else {
		textPartHeaders, textPartData := createTextPart(email)
		textPart, err := writer.CreatePart(textPartHeaders)
		if err != nil {
			panic(err)
		}
		textPart.Write(textPartData)
	}

	for _, att := range email.Attachments {
		if att.AttachmentType != template.AttachmentTypeAttachment {
			continue
		}
		err := att.MakeMIMEPart(writer)
		if err != nil {
			panic(err)
		}
	}

	writer.Close()
	return buf.Bytes()
}

func createAlternativePart(email *email.Email) (textproto.MIMEHeader, []byte) {
	buf := bytes.Buffer{}
	header := make(textproto.MIMEHeader)

	altWriter := multipart.NewWriter(&buf)

	header.Set("Content-Type", fmt.Sprintf("multipart/alternative; boundary=%s", altWriter.Boundary()))

	textPartHeaders, textPartData := createTextPart(email)
	textPart, err := altWriter.CreatePart(textPartHeaders)
	if err != nil {
		panic(err)
	}
	textPart.Write(textPartData)

	htmlPartHeaders, htmlPartData := createHTMLPart(email)
	htmlPart, err := altWriter.CreatePart(htmlPartHeaders)
	if err != nil {
		panic(err)
	}
	htmlPart.Write(htmlPartData)

	altWriter.Close()
	return header, buf.Bytes()
}

func createTextPart(email *email.Email) (textproto.MIMEHeader, []byte) {
	header := make(textproto.MIMEHeader)
	header.Set("Content-Type", "text/plain")
	header.Set("Content-Transfer-Encoding", "quoted-printable")
	buf := bytes.Buffer{}
	qpWriter := quotedprintable.NewWriter(&buf)
	qpWriter.Write([]byte(email.Text))
	qpWriter.Close()
	return header, buf.Bytes()
}

func createHTMLPart(email *email.Email) (textproto.MIMEHeader, []byte) {
	buf := bytes.Buffer{}
	header := make(textproto.MIMEHeader)

	relatedWriter := multipart.NewWriter(&buf)

	htmlPartHeader := make(textproto.MIMEHeader)
	htmlPartHeader.Set("Content-Type", "text/html")
	htmlPartHeader.Set("Content-Transfer-Encoding", "quoted-printable")
	htmlPartWriter, err := relatedWriter.CreatePart(htmlPartHeader)
	if err != nil {
		panic(err)
	}

	qpWriter := quotedprintable.NewWriter(htmlPartWriter)
	qpWriter.Write([]byte(email.HTML))
	qpWriter.Close()

	for _, att := range email.Attachments {
		if att.AttachmentType != template.AttachmentTypeInline {
			continue
		}
		err = att.MakeMIMEPart(relatedWriter)
		if err != nil {
			panic(err)
		}
	}

	relatedWriter.Close()

	header.Set("Content-Type", fmt.Sprintf("multipart/related; boundary=%s", relatedWriter.Boundary()))

	return header, buf.Bytes()
}
