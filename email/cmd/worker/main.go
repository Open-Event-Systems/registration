package main

import (
	"context"
	"email/config"
	"email/email"
	"email/senders"
	"email/template"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatalf("usage: %s <config file>", os.Args[0])
	}

	cfg := config.LoadConfig(os.Args[1])
	env := template.NewEnvironment(cfg)
	sender := senders.GetSender(cfg)

	conn, err := connect(cfg.AMQP_URL)
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	channel, err := conn.Channel()
	if err != nil {
		panic(err)
	}
	defer channel.Close()

	err = channel.ExchangeDeclare("email", amqp.ExchangeTopic, true, false, false, false, nil)
	if err != nil {
		panic(err)
	}

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	wg := sync.WaitGroup{}
	for emailType, msgCfg := range cfg.Messages {
		emailType_ := emailType
		consumeChan, err := consumeQueue(ctx, cfg, &msgCfg, conn, emailType, env, sender)
		if err != nil {
			log.Printf("failed to consume email queue %s: %v", emailType, err)
			continue
		}

		wg.Add(1)
		go func() {
			defer wg.Done()
			err := <-consumeChan
			if err != nil {
				log.Printf("consumer for email queue %s exited: %v", emailType_, err)
			} else {
				log.Printf("consumer for email queue %s exited", emailType_)
			}
		}()
	}

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt)
	go func() {
		<-sigChan
		signal.Reset(os.Interrupt)
		cancel()
	}()

	wg.Wait()
	channel.Close()
	conn.Close()
}

func connect(url string) (*amqp.Connection, error) {
	var conn *amqp.Connection
	var err error
	for i := 0; i < 5; i++ {
		if i != 0 {
			time.Sleep(5 * time.Second)
		}

		conn, err = amqp.Dial(url)
		if err == nil {
			return conn, err
		}
	}
	return nil, err
}

func consumeQueue(context context.Context, config *config.Config, msgConfig *config.MessageConfig, conn *amqp.Connection, emailType string, env *template.TemplateEnvironment, sender email.Sender) (<-chan error, error) {
	channel, err := conn.Channel()
	if err != nil {
		return nil, err
	}

	err = channel.Qos(1, 0, false)
	if err != nil {
		channel.Close()
		return nil, err
	}

	queueName := fmt.Sprintf("email.%s", emailType)
	_, err = channel.QueueDeclare(queueName, true, false, false, false, nil)
	if err != nil {
		channel.Close()
		return nil, err
	}
	err = channel.QueueBind(queueName, queueName, "email", false, nil)
	if err != nil {
		channel.Close()
		return nil, err
	}

	errChan := make(chan error, 1)

	go func() {
		defer close(errChan)
		defer channel.Close()
		deliveries, err := channel.ConsumeWithContext(context, queueName, "", false, false, false, false, nil)
		if err != nil {
			errChan <- err
			return
		}

		log.Printf("consuming email queue %s", emailType)
		for msg := range deliveries {
			err = sendMessage(emailType, config, msgConfig, msg.Body, env, sender)
			if err == nil {
				msg.Ack(false)
			} else {
				log.Printf("error sending message: %v", err)
				msg.Reject(false)
			}
		}
	}()
	return errChan, nil
}

func sendMessage(emailType string, config *config.Config, msgCfg *config.MessageConfig, data []byte, env *template.TemplateEnvironment, sender email.Sender) error {
	var msgJson map[string]interface{}

	err := json.Unmarshal(data, &msgJson)
	if err != nil {
		return err
	}

	to, toOk := msgJson["to"].(string)
	if !toOk || to == "" {
		return errors.New("missing \"to\"")
	}

	tmplInput := &template.TemplateInput{
		To:      to,
		From:    msgCfg.From,
		Subject: msgCfg.Subject,
		Data:    msgJson,
	}

	if tmplInput.From == "" {
		tmplInput.From = config.From
	}

	result := env.Render(emailType, tmplInput)

	email := &email.Email{
		From:        tmplInput.From,
		To:          tmplInput.To,
		Subject:     tmplInput.Subject,
		Attachments: result.Attachments.Attachments,
		Text:        result.Text,
		HTML:        result.HTML,
	}

	err = sender.Send(email)
	if err != nil {
		return err
	}
	log.Printf("sent %s message to %s", emailType, tmplInput.To)
	return nil
}
