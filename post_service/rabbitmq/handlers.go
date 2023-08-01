package rabbitmq

import (
	"database/sql"
	"fmt"
	"service/database"
	"service/logger"
	"time"

	"github.com/google/uuid"
)

func HandleVote(db *sql.DB, e VoteEvent) error {
	if e.PostUUID == "" || e.VoterUUID == "" || (e.Type != Upvote && e.Type != Downvote) {
		logger.Log("error", fmt.Sprintf("Invalid vote event: %v", e), "rabbitmq/handlers.go", "")
		return fmt.Errorf("invalid vote event: %v", e)
	}

	var magnitude int

	if e.Type == Upvote {
		magnitude = 1
	} else if e.Type == Downvote {
		magnitude = -1
	} else {
		logger.Log("error", fmt.Sprintf("Invalid vote type: %s", e.Type), "rabbitmq/rabbitmq.go", "")
		return fmt.Errorf("invalid vote type: %s", e.Type)
	}

	err := database.UpdateVoteCount(db, e.PostUUID, magnitude)
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to update vote count: %v", err), "rabbitmq/rabbitmq.go", "")
		return err
	}

	return nil
}

func HandlePost(db *sql.DB, e PostEvent) error {
	if e.CreatorUUID == "" || e.Title == "" || e.URL == "" {
		logger.Log("error", fmt.Sprintf("Invalid post event: %v", e), "rabbitmq/handlers.go", "")
		return fmt.Errorf("invalid post event: %v", e)
	}

	newUUID := uuid.New().String()

	post := database.Post{
		PostUUID:    newUUID,
		CreatorUUID: e.CreatorUUID,
		VoteCount:   0,
		Title:       e.Title,
		URL:         e.URL,
		CreatedAt:   time.Now().Format(time.RFC3339),
	}

	err := database.InsertPost(db, post)
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to insert post: %v", err), "rabbitmq/rabbitmq.go", "")
		return err
	}

	return nil
}
