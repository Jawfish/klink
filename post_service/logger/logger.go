package logger

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"runtime"
	"strconv"

	"github.com/fluent/fluent-logger-golang/fluent"
)

type LogLevel string

const (
	Debug LogLevel = "debug"
	Info  LogLevel = "info"
	Warn  LogLevel = "warn"
	Error LogLevel = "error"
)

var Fluentd *fluent.Fluent

func InitLogger() {
	port, err := strconv.Atoi(os.Getenv("FLUENTD_PORT"))
	if err != nil {
		log.Printf("Failed to parse Fluentd port: %v", err)
	}

	config := fluent.Config{
		FluentPort: port,
		FluentHost: os.Getenv("FLUENTD_HOST"),
	}

	Fluentd, err = fluent.New(config)
	if err != nil {
		log.Printf("Failed to connect to Fluentd: %v", err)
	}
}

func Log(level LogLevel, message string, where string, stackTrace string) {
	_, file, line, _ := runtime.Caller(1)

	logMessage := fmt.Sprintf("%s | %s | %s:%d | %s", level, message, file, line, stackTrace)

	fmt.Println(logMessage)

	data := map[string]string{
		"host":        os.Getenv("HOSTNAME"),
		"level":       string(level),
		"message":     message,
		"where":       fmt.Sprintf("%s:%d", file, line),
		"stack_trace": stackTrace,
	}

	if Fluentd != nil {
		error := Fluentd.Post(os.Getenv("FLUENTD_TAG"), data)
		if error != nil {
			log.Printf("Failed to post log to Fluentd: %v", error)
		}
	}
}

func LogRequestHandler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		queryParams := r.URL.Query().Encode()

		Log("info", fmt.Sprintf("Received request: %s %s?%s", r.Method, r.URL.Path, queryParams), "logger/logger.go", "")

		recorder := &responseRecorder{ResponseWriter: w}
		next.ServeHTTP(recorder, r)

		Log("info", fmt.Sprintf("Response: %d", recorder.statusCode), "logger/logger.go", "")
	})
}

type responseRecorder struct {
	http.ResponseWriter
	statusCode int
}

func (r *responseRecorder) WriteHeader(statusCode int) {
	r.statusCode = statusCode
	r.ResponseWriter.WriteHeader(statusCode)
}
