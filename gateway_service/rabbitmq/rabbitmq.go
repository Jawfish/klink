package rabbitmq

import (
	"fmt"
	"os"
	"time"

	"github.com/streadway/amqp"
)

type RabbitMQ struct {
	Connection *amqp.Connection
}

func NewRabbitMQ() (*RabbitMQ, error) {
	rabbitMQURL := fmt.Sprintf(
		"amqp://%s:%s@%s:%s/",
		os.Getenv("RABBITMQ_USER"),
		os.Getenv("RABBITMQ_PASS"),
		os.Getenv("RABBITMQ_HOST"),
		os.Getenv("RABBITMQ_PORT"),
	)

	var conn *amqp.Connection
	var err error

	for {
		conn, err = amqp.Dial(rabbitMQURL)
		if err == nil {
			break
		}

		fmt.Printf("Could not connect to RabbitMQ, retrying in 3 seconds: %v", err)
		time.Sleep(3 * time.Second)
	}

	return &RabbitMQ{Connection: conn}, nil
}

func (r *RabbitMQ) SendToQueue(queueName string, msg string) error {
	channel, err := r.Connection.Channel()
	if err != nil {
		return err
	}
	defer channel.Close()

	_, err = channel.QueueDeclare(
		queueName, // name of the queue
		true,      // durable
		false,     // delete when unused
		false,     // exclusive
		false,     // no-wait
		nil,       // arguments
	)
	if err != nil {
		return err
	}

	return channel.Publish(
		"",
		queueName,
		false,
		false,
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(msg),
		})
}
