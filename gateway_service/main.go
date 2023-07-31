package main

import (
	"service/config"
	"service/server"
)

func main() {
	config.LoadEnv()
	server.Run()
}
