package main

import (
	"github.com/google/uuid"
)

type UserContext struct {
	UUID     uuid.UUID `json:"uuid"`
	Username string    `json:"username"`
}
