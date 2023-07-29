package logger

import (
	"fmt"
	"log"
	"os"
	"runtime"
	"strconv"

	"github.com/fluent/fluent-logger-golang/fluent"
)

var Fluentd *fluent.Fluent

func InitLogger() {
	port, err := strconv.Atoi(os.Getenv("FLUENTD_PORT"))
	if err != nil {
		log.Fatalf("Failed to parse Fluentd port: %v", err)
	}

	config := fluent.Config{
		FluentPort: port,
		FluentHost: os.Getenv("FLUENTD_HOST"),
	}

	Fluentd, err = fluent.New(config)
	if err != nil {
		log.Fatalf("Failed to connect to Fluentd: %v", err)
	}
}

func Log(level string, message string, where string, stackTrace string) {
	_, file, line, _ := runtime.Caller(1)

	logMessage := fmt.Sprintf("%s | %s | %s:%d | %s", level, message, file, line, stackTrace)

	fmt.Println(logMessage)

	data := map[string]string{
		"host":        os.Getenv("HOSTNAME"),
		"level":       level,
		"message":     message,
		"where":       fmt.Sprintf("%s:%d", file, line),
		"stack_trace": stackTrace,
	}

	error := Fluentd.Post(os.Getenv("FLUENTD_TAG"), data)
	if error != nil {
		log.Fatalf("Failed to post log to Fluentd: %v", error)
	}
}
