package main

import (
	"fmt"
	"log"
	"net/http"

	"gateway_service/routes"
)

const port = 8080

func main() {
	log.Printf("Starting server at http://localhost:%d", port)

	err := http.ListenAndServe(fmt.Sprintf(":%d", port), routes.Router())

	if err != nil {
		log.Fatal(err)
	}
}
