package routes

import (
	"net/http"

	"gateway_service/handlers"
)

func Router() http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("/", handlers.LoginHandler)

	return mux
}
