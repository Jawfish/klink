package rabbitmq

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	database "service/db"
	"service/logger"
	"service/utils"
	"time"

	"github.com/streadway/amqp"
)

func StartConsumer(db *sql.DB) {
	logger.Log("info", "Starting RabbitMQ consumer...", "rabbitmq/rabbitmq.go", "")
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

	defer conn.Close()

	logger.Log("info", "Opening RabbitMQ channel...", "rabbitmq/rabbitmq.go", "")
	ch, err := conn.Channel()
	utils.FailOnError(err, "Failed to open a channel")
	logger.Log("info", "Successfully opened RabbitMQ channel.", "rabbitmq/rabbitmq.go", "")
	defer ch.Close()

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

	forever := make(chan bool)

	go func() {
		for d := range msgs {
			logger.Log("info", fmt.Sprintf("Received a message: %s", d.Body), "rabbitmq/rabbitmq.go", "")
			var post database.Post
			err := json.Unmarshal(d.Body, &post)
			if err != nil {
				logger.Log("error", fmt.Sprintf("Error decoding JSON: %s", err), "rabbitmq/rabbitmq.go", "")
			} else {
				logger.Log("info", fmt.Sprintf("Decoded post: %v", post), "rabbitmq/rabbitmq.go", "")
				database.InsertPost(db, post)
				logger.Log("info", "Successfully inserted post into the database.", "rabbitmq/rabbitmq.go", "")
			}
		}
	}()

	logger.Log("info", " [*] Waiting for messages. To exit press CTRL+C", "rabbitmq/rabbitmq.go", "")
	<-forever
}
