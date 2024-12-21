package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"sheets_hook/internal/api"
	"sheets_hook/internal/config"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

const EXCHANGE_NAME = "registration"
const QUEUE_NAME = "sheets"

func main() {
	if len(os.Args) != 2 {
		log.Fatalf("usage: %s <config file>", os.Args[0])
	}

	config := config.LoadConfig(os.Args[1])

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	client, err := api.MakeClient(ctx, config)
	if err != nil {
		panic(err)
	}

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

	errChan := consume(config, client, ctx, channel)

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

func consume(config *config.Config, client *api.Client, ctx context.Context, channel *amqp.Channel) <-chan error {
	errChan := make(chan error, 1)
	go func() {
		defer close(errChan)
		waiter := api.Waiter{}
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
				log.Printf("error handling message: %v\n", err)
				msg.Reject(false)
				continue
			}

			jsonBytes, err := json.Marshal(data["new"])
			if err != nil {
				log.Printf("error handling message: %v\n", err)
				msg.Reject(false)
				continue
			}

			data["json"] = string(jsonBytes)

			id := data["id"]
			log.Printf("handling update for %v\n", id)

			cols := config.Columns.EvaluateColumns(data)
			err = retryAppend(ctx, client, &waiter, cols)
			if err != nil {
				log.Printf("error appending row: %v\n", err)
				msg.Reject(!msg.Redelivered)
				continue
			}

			waiter.Reset()

			msg.Ack(false)
		}
	}()

	return errChan
}

func retryAppend(ctx context.Context, client *api.Client, waiter *api.Waiter, cols []any) error {
	for {
		err := client.Append(cols)
		if err != nil {
			if api.IsRateLimitError(err) {
				log.Print("rate limit exceeded, waiting and retrying\n")
				waiter.Wait(ctx)
			} else {
				return err
			}
		} else {
			return nil
		}
	}
}
