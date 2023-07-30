package rabbitmq

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"service/logger"
	"service/utils"
	"time"

	"github.com/streadway/amqp"
)

func ConnectToRabbitMQ() (*amqp.Connection, error) {
	var conn *amqp.Connection
	var err error

	attempts := 0
	for {
		logger.Log("info", fmt.Sprintf("Attempting to connect to RabbitMQ (attempt %d)...", attempts+1), "rabbitmq/rabbitmq.go", "")
		conn, err = amqp.Dial(fmt.Sprintf("amqp://%s:%s@%s:%s/",
			os.Getenv("RABBITMQ_USER"),
			os.Getenv("RABBITMQ_PASS"),
			os.Getenv("RABBITMQ_HOST"),
			os.Getenv("RABBITMQ_PORT")))

		if err == nil {
			logger.Log("info", "Successfully connected to RabbitMQ.", "rabbitmq/rabbitmq.go", "")
			break
		}

		attempts++
		if attempts >= 5 {
			utils.FailOnError(err, "Failed to connect to RabbitMQ")
		}

		logger.Log("info", fmt.Sprintf("Could not connect to RabbitMQ (attempt %d), retrying in 5 seconds", attempts), "rabbitmq/rabbitmq.go", "")
		time.Sleep(5 * time.Second)
	}

	return conn, err
}

func OpenChannel(conn *amqp.Connection) (*amqp.Channel, error) {
	logger.Log("info", "Opening RabbitMQ channel...", "rabbitmq/rabbitmq.go", "")
	ch, err := conn.Channel()
	utils.FailOnError(err, "Failed to open a channel")
	logger.Log("info", "Successfully opened RabbitMQ channel.", "rabbitmq/rabbitmq.go", "")
	return ch, err
}

func declareQueue(ch *amqp.Channel) (amqp.Queue, error) {

	logger.Log("info", "Declaring RabbitMQ queue...", "rabbitmq/rabbitmq.go", "")
	queue, err := ch.QueueDeclare(
		os.Getenv("RABBITMQ_QUEUE"), // name of the queue
		true,                        // durable
		false,                       // delete when unused
		false,                       // exclusive
		false,                       // no-wait
		nil,                         // arguments
	)

	utils.FailOnError(err, "Failed to declare a queue")
	logger.Log("info", "Successfully declared RabbitMQ queue.", "rabbitmq/rabbitmq.go", "")

	return queue, err
}
func registerConsumer(ch *amqp.Channel, queue amqp.Queue) (<-chan amqp.Delivery, error) {
	logger.Log("info", "Registering RabbitMQ consumer...", "rabbitmq/rabbitmq.go", "")
	msgs, err := ch.Consume(
		queue.Name,
		"",    // consumer
		true,  // auto-ack
		false, // exclusive
		false, // no-local
		false, // no-wait
		nil,   // args
	)
	utils.FailOnError(err, "Failed to register a consumer")
	logger.Log("info", "Successfully registered RabbitMQ consumer.", "rabbitmq/rabbitmq.go", "")

	return msgs, err
}

func consumeMessages(db *sql.DB, msgs <-chan amqp.Delivery) {
	handlers := map[string]func(*sql.DB, []byte) error{
		string(Upvote): func(db *sql.DB, body []byte) error {
			var event VoteEvent
			if err := json.Unmarshal(body, &event); err != nil {
				return err
			}
			return HandleVote(db, event)
		},
		string(Downvote): func(db *sql.DB, body []byte) error {
			var event VoteEvent
			if err := json.Unmarshal(body, &event); err != nil {
				return err
			}
			return HandleVote(db, event)
		},
		string(LinkPost): func(db *sql.DB, body []byte) error {
			var event PostEvent
			if err := json.Unmarshal(body, &event); err != nil {
				return err
			}
			return HandlePost(db, event)
		},
	}

	go func() {
		for d := range msgs {
			var event struct {
				Type string `json:"type"`
			}

			// determine the event type
			if err := json.Unmarshal(d.Body, &event); err != nil {
				logger.Log("error", fmt.Sprintf("Error decoding JSON: %s", err), "rabbitmq/rabbitmq.go", "")
				continue
			}

			// find and execute the right handler
			if handler, ok := handlers[event.Type]; ok {
				if err := handler(db, d.Body); err != nil {
					logger.Log("error", fmt.Sprintf("Error handling '%s' event: %v", event.Type, err), "rabbitmq/rabbitmq.go", "")
				}
			} else {
				logger.Log("warning", fmt.Sprintf("No handler for '%s' event", event.Type), "rabbitmq/rabbitmq.go", "")
			}
		}
	}()
}

func StartConsumer(db *sql.DB, conn *amqp.Connection, ch *amqp.Channel) {
	logger.Log("info", "Starting RabbitMQ consumer...", "rabbitmq/rabbitmq.go", "")

	defer conn.Close()
	defer ch.Close()

	queue, err := declareQueue(ch)
	utils.FailOnError(err, "Failed to declare a queue")

	msgs, err := registerConsumer(ch, queue)
	utils.FailOnError(err, "Failed to register a consumer")

	go consumeMessages(db, msgs)

	logger.Log("info", " [*] Waiting for messages. To exit press CTRL+C", "rabbitmq/rabbitmq.go", "")
	forever := make(chan bool)
	<-forever
}
