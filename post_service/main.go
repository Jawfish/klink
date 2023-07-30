package main

import (
	"log"

	"service/config"
	database "service/db"
	"service/logger"
	"service/rabbitmq"
	"service/utils"
)

func main() {
	config.LoadEnv()
	logger.InitLogger()

	db := database.OpenDatabase(":memory:")
	database.StartDatabase(db)

	conn, err := rabbitmq.ConnectToRabbitMQ()
	utils.FailOnError(err, "Failed to connect to RabbitMQ")

	ch, err := rabbitmq.OpenChannel(conn)
	utils.FailOnError(err, "Failed to open a channel")

	rabbitmq.StartConsumer(db, conn, ch)
	defer db.Close()
	log.Println("Done.")
}
