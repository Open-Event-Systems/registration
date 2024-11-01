package senders

import (
	"email/config"
	"email/email"
	"email/senders/mock"
	"email/senders/smtp"
)

func GetSender(cfg *config.Config) email.Sender {
	switch cfg.Use {
	case "smtp":
		return smtp.NewSMTPSender(&cfg.SMTPConfig)
	default:
		return mock.NewMockSender()
	}
}
