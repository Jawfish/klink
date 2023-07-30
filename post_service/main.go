package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	"service/api"
	"service/config"
	"service/database"
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

	go startHTTPServer(db)
	rabbitmq.StartConsumer(db, conn, ch)

	defer db.Close()
	logger.Log(logger.Info, "Service shutdown.", "main.go", "")
}

func startHTTPServer(db *sql.DB) {
	api.SetupRoutes(db)

	host := os.Getenv("HOST_IP")
	port := os.Getenv("HOST_PORT")
	addr := fmt.Sprintf("%s:%s", host, port)

	server := &http.Server{
		Addr:    addr,
		Handler: logger.LogRequestHandler(http.DefaultServeMux),
	}

	logger.Log("info", fmt.Sprintf("Starting API server at http://%s", addr), "main.go", "")

	log.Fatal(server.ListenAndServe())
}
