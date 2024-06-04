package main

import (
	"email/config"
	"email/email"
	"email/senders"
	"email/template"
	"encoding/json"
	"io"
	"log"
	"os"
)

func main() {
	if len(os.Args) != 3 {
		log.Fatalf("usage: %s <config file> <type>", os.Args[0])
	}

	cfg := config.LoadConfig(os.Args[1])
	env := template.NewEnvironment(cfg)

	emailType := os.Args[2]

	emailConfig, emailOk := cfg.Messages[emailType]
	if !emailOk {
		log.Fatalf("email type not found: %s", emailType)
	}

	inputBytes, err := io.ReadAll(os.Stdin)
	if err != nil {
		panic(err)
	}

	var inputData map[string]interface{}
	err = json.Unmarshal(inputBytes, &inputData)
	if err != nil {
		panic(err)
	}

	to, toOk := inputData["to"].(string)
	if !toOk {
		log.Fatal("missing \"to\"")
	}

	input := &template.TemplateInput{
		To:      to,
		From:    emailConfig.From,
		Subject: emailConfig.Subject,
		Data:    inputData,
	}

	if input.From == "" {
		input.From = cfg.From
	}

	tmplResult := env.Render(emailType, input)
	email := &email.Email{
		From:        input.From,
		To:          input.To,
		Subject:     input.Subject,
		Attachments: tmplResult.Attachments.Attachments,
		Text:        tmplResult.Text,
		HTML:        tmplResult.HTML,
	}

	sender := senders.GetSender(cfg)
	err = sender.Send(email)
	if err != nil {
		panic(err)
	}

}
