package rabbitmq

import (
	"database/sql"
	"fmt"
	"service/database"
	"service/logger"
	"time"
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

	logger.Log("info", fmt.Sprintf("Successfully updated vote count for post: %s", e.PostUUID), "rabbitmq/rabbitmq.go", "")

	return nil
}

func HandlePost(db *sql.DB, e PostEvent) error {
	if e.UUID == "" || e.Title == "" || e.URL == "" {
		logger.Log("error", fmt.Sprintf("Invalid post event: %v", e), "rabbitmq/handlers.go", "")
		return fmt.Errorf("invalid post event: %v", e)
	}

	post := database.Post{
		UUID:      e.UUID,
		Author:    "unknown", // TODO: get from auth service
		VoteCount: 0,
		Title:     e.Title,
		URL:       e.URL,
		CreatedAt: time.Now().Format(time.RFC3339),
	}

	err := database.InsertPost(db, post)
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to insert post: %v", err), "rabbitmq/rabbitmq.go", "")
		return err
	}

	logger.Log("info", fmt.Sprintf("Successfully inserted post: %v", e), "rabbitmq/rabbitmq.go", "")
	return nil
}
