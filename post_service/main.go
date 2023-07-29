package main

import (
	"log"

	"service/config"
	database "service/db"
	"service/logger"
	"service/rabbitmq"
)

func main() {
	config.LoadEnv()
	logger.InitLogger()
	db := database.OpenDatabase(":memory:")
	database.StartDatabase(db)
	rabbitmq.StartConsumer(db)
	defer db.Close()
	log.Println("Done.")
}
