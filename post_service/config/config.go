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
