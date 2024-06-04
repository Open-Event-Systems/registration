package senders

import (
	"email/config"
	"email/email"
	"email/senders/mock"
)

func GetSender(cfg *config.Config) email.Sender {
	switch cfg.Use {
	default:
		return mock.NewMockSender()
	}
}
