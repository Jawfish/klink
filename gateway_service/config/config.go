package config

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

func LoadEnv() {
	err := godotenv.Load()

	if err != nil {
		log.Print("Error loading .env file, falling back to environment variables")
	}

	vars := []string{
		"HOST_PORT",
		"HOST_IP",
		"AUTH_SERVICE_HOST",
		"AUTH_SERVICE_PORT",
		"POST_SERVICE_HOST",
		"POST_SERVICE_PORT",
		"USER_SERVICE_HOST",
		"USER_SERVICE_PORT",
		"RABBITMQ_HOST",
		"RABBITMQ_PORT",
		"RABBITMQ_USER",
		"RABBITMQ_PASS",
		"RABBITMQ_POST_SERVICE_QUEUE",
		"FLUENTD_HOST",
		"FLUENTD_PORT",
		"FLUENTD_TAG",
		"LOG_TO_STDOUT",
	}

	for _, v := range vars {
		_, exists := os.LookupEnv(v)

		if !exists {
			log.Fatalf("Environment variable %s is not set", v)
		}
	}
}
