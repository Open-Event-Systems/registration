package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"print/internal/config"
	"print/internal/document"
	"time"

	"github.com/nikolalohinski/gonja/v2"
	"github.com/nikolalohinski/gonja/v2/loaders"
	amqp "github.com/rabbitmq/amqp091-go"
)

const EXCHANGE_NAME = "registration"
const QUEUE_NAME = "print"

func main() {

	if len(os.Args) != 2 {
		log.Fatalf("usage: %s <config file>", os.Args[0])
	}

	config := config.LoadConfig(os.Args[1])
	eventDocTypes := config.LoadEventDocumentTypes(
		gonja.DefaultConfig,
		loaders.MustNewFileSystemLoader("."),
		gonja.DefaultEnvironment,
	)

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	conn, err := connect(config)
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	channel, err := conn.Channel()
	if err != nil {
		panic(err)
	}
	defer channel.Close()

	err = channel.Qos(1, 0, false)
	if err != nil {
		panic(err)
	}

	err = channel.ExchangeDeclare(EXCHANGE_NAME, amqp.ExchangeTopic, true, false, false, false, nil)
	if err != nil {
		panic(err)
	}

	_, err = channel.QueueDeclare(QUEUE_NAME, true, false, false, false, nil)
	if err != nil {
		panic(err)
	}

	err = channel.QueueBind(QUEUE_NAME, "update.*", EXCHANGE_NAME, false, nil)
	if err != nil {
		panic(err)
	}

	errChan := consume(config, eventDocTypes, ctx, channel)

	select {
	case err = <-errChan:
		if err != nil {
			log.Fatalf("exiting: %v\n", err)
		} else {
			log.Println("exiting")
		}
	case <-ctx.Done():
		log.Println("exiting")
	}
	<-errChan
}

func connect(config *config.Config) (*amqp.Connection, error) {
	var conn *amqp.Connection
	var err error

	for i := 0; i < 5; i++ {
		if i != 0 {
			time.Sleep(5 * time.Second)
		}
		conn, err = amqp.Dial(config.AMQPURL)
		if err == nil {
			return conn, err
		}
	}

	return nil, err
}

func consume(config *config.Config, eventDocTypes map[string]map[string]*document.DocumentType, ctx context.Context, channel *amqp.Channel) <-chan error {
	errChan := make(chan error, 1)
	go func() {
		defer close(errChan)
		deliveryChan, err := channel.ConsumeWithContext(ctx, QUEUE_NAME, "", false, false, false, false, nil)
		log.Println("listening to update queue")
		if err != nil {
			errChan <- err
			return
		}

		for msg := range deliveryChan {
			var data map[string]any

			err := json.Unmarshal(msg.Body, &data)
			if err != nil {
				log.Printf("error handling message: %v", err)
				msg.Reject(false)
				continue
			}

			id := data["id"].(string)
			log.Printf("handling update for %v", id)
			updateDocuments(config.PrintURL, eventDocTypes, data)
			msg.Ack(false)
		}
	}()

	return errChan
}

func updateDocuments(printURL string, eventDocTypes map[string]map[string]*document.DocumentType, data map[string]any) {
	new := data["new"].(map[string]any)
	eventId := new["event_id"].(string)
	id := new["id"].(string)
	docTypes := eventDocTypes[eventId]
	if docTypes == nil {
		return
	}

	for _, typ := range docTypes {
		updateDocument(printURL, eventId, id, typ, data)
	}
}

func updateDocument(printURL string, eventId string, id string, docType *document.DocumentType, data map[string]any) {
	registration := data["new"].(map[string]any)
	if !docType.EvaluateCondition(registration) {
		return
	}
	hash, err := docType.GetHash(registration)
	if err != nil {
		return
	}

	docUrl := fmt.Sprintf("%s/events/%s/registrations/%s/documents/%s/%s.pdf", printURL, eventId, id, docType.Id, hash)
	res, err := http.Get(docUrl)
	if err != nil {
		log.Printf("error updating %s/%s/%s: %v", eventId, id, docType.Id, err)
		return
	}
	defer res.Body.Close()

	if res.StatusCode != 200 {
		log.Printf("error updating %s/%s/%s: http %d", eventId, id, docType.Id, res.StatusCode)
		return
	}

	docData, err := io.ReadAll(res.Body)
	if err != nil {
		log.Printf("error updating %s/%s/%s: %v", eventId, id, docType.Id, err)
		return
	}

	for _, printCfg := range docType.Print {
		printDocument(&printCfg, eventId, id, docType, docData, data)
	}
}

func printDocument(printCfg *document.PrintConfig, eventId string, id string, docType *document.DocumentType, fileData []byte, data map[string]any) {
	if !printCfg.EvaluateCondition(data) {
		return
	}
	tmpf, err := os.CreateTemp("", "print-*.pdf")
	if err != nil {
		log.Printf("error submitting print job: %v", err)
		return
	}
	defer os.Remove(tmpf.Name())
	defer tmpf.Close()

	_, err = tmpf.Write(fileData)
	if err != nil {
		log.Printf("error submitting print job: %v", err)
		return
	}
	tmpf.Close()

	err = printCfg.Submit(tmpf.Name())
	if err != nil {
		log.Printf("error submitting print job: %v", err)
		return
	}

	log.Printf("submitted %s/%s/%s to %s/%s", eventId, id, docType.Id, printCfg.Server, printCfg.Destination)
}
