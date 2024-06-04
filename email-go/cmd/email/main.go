package main

import (
	"email/config"
	"email/email"
	"email/senders"
	"log"
	"os"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatalf("usage: %s <config file>", os.Args[0])
	}

	cfg := config.LoadConfig(os.Args[1])
	log.Printf("value %v", cfg)

	sender := senders.GetSender(cfg)
	sender.Send(&email.Email{
		From: "from@example.net",
		To: "to@example.net",
		Subject: "Test Subject",
		Text: "Example message",
	})

}
