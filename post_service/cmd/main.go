package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/joho/godotenv"
	_ "github.com/mattn/go-sqlite3"
	"github.com/streadway/amqp"
)

func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}
func main() {
	loadEnv()

	var conn *amqp.Connection
	var err error

	attempts := 0
	// rabbitmqHost := os.Getenv("RABBITMQ_HOST")
	// rabbitmqPort := os.Getenv("RABBITMQ_PORT")
	// rabbitmqUser := os.Getenv("RABBITMQ_USER")
	// rabbitmqPass := os.Getenv("RABBITMQ_PASS")
	for {
		// conn, err = amqp.Dial("amqp://guest:guest@rabbitmq:5672/")
		conn, err = amqp.Dial(fmt.Sprintf("amqp://%s:%s@%s:%s/",
			os.Getenv("RABBITMQ_USER"),
			os.Getenv("RABBITMQ_PASS"),
			os.Getenv("RABBITMQ_HOST"),
			os.Getenv("RABBITMQ_PORT")))

		if err == nil {
			break
		}

		attempts++
		if attempts >= 5 {
			failOnError(err, "Failed to connect to RabbitMQ")
		}

		log.Printf("Could not connect to RabbitMQ (attempt %d), retrying in 5 seconds", attempts)
		time.Sleep(5 * time.Second)
	}

	defer conn.Close()

	ch, err := conn.Channel()
	failOnError(err, "Failed to open a channel")
	defer ch.Close()

	queue, err := ch.QueueDeclare(
		os.Getenv("RABBITMQ_QUEUE"), // name of the queue
		true,                        // durable
		false,                       // delete when unused
		false,                       // exclusive
		false,                       // no-wait
		nil,                         // arguments
	)

	failOnError(err, "Failed to declare a queue")

	msgs, err := ch.Consume(
		queue.Name,
		"",    // consumer
		true,  // auto-ack
		false, // exclusive
		false, // no-local
		false, // no-wait
		nil,   // args
	)
	failOnError(err, "Failed to register a consumer")

	forever := make(chan bool)

	go func() {
		for d := range msgs {
			log.Printf("Received a message: %s", d.Body)
		}
	}()

	log.Printf(" [*] Waiting for messages. To exit press CTRL+C")
	<-forever

	log.Println("Opening database...")
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		log.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	log.Println("Creating table...")
	statement, err := db.Prepare("CREATE TABLE IF NOT EXISTS people (id INTEGER PRIMARY KEY, firstname TEXT, lastname TEXT)")
	if err != nil {
		log.Fatalf("Failed to prepare statement: %v", err)
	}
	statement.Exec()

	log.Println("Inserting data...")
	statement, err = db.Prepare("INSERT INTO people (firstname, lastname) VALUES (?, ?)")
	if err != nil {
		log.Fatalf("Failed to prepare statement: %v", err)
	}
	statement.Exec("John", "Doe")

	log.Println("Querying data...")
	rows, err := db.Query("SELECT firstname, lastname FROM people")
	if err != nil {
		log.Fatalf("Failed to query data: %v", err)
	}
	var firstName string
	var lastName string
	for rows.Next() {
		rows.Scan(&firstName, &lastName)
		fmt.Println(firstName, lastName)
	}

	log.Println("Done.")
}

func loadEnv() {
	err := godotenv.Load()

	if err != nil {
		log.Print("Error loading .env file, falling back to environment variables")
	}

	vars := []string{
		"HOST_PORT",
		"HOST_IP",
		"DB_HOST",
		"DB_PORT",
		"DB_USER",
		"DB_PASS",
		"DB_NAME",
		"RABBITMQ_HOST",
		"RABBITMQ_PORT",
		"RABBITMQ_USER",
		"RABBITMQ_PASS",
		"RABBITMQ_QUEUE",
		"FLUENTD_HOST",
		"FLUENTD_PORT",
		"FLUENTD_TAG",
	}

	for _, v := range vars {
		_, exists := os.LookupEnv(v)

		if !exists {
			log.Fatalf("Environment variable %s is not set", v)
		}
	}
}
