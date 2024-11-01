package mock

import (
	"email/email"
	"log"
)

type mockSender struct{}

func NewMockSender() *mockSender {
	return &mockSender{}
}

func (s *mockSender) Send(email *email.Email) error {
	log.Printf("Mock sending email:\nFrom: %s\nTo: %s\nSubject: %s\n\n%s", email.From, email.To, email.Subject, email.Text)
	return nil
}
