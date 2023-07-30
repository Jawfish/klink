package db

import (
	"database/sql"
	"fmt"
	"service/logger"

	_ "github.com/mattn/go-sqlite3"
)

func InsertPost(db *sql.DB, post Post) error {
	if db == nil {
		return fmt.Errorf("database connection is not established")
	}

	logger.Log("info", fmt.Sprintf("Inserting post: %v", post), "db/db.go", "")
	statement, err := db.Prepare("INSERT INTO posts (uuid, author, votecount, title, url, createdat) VALUES (?, ?, ?, ?, ?, ?)")
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to prepare statement: %v", err), "db/db.go", "")
		return err
	}

	_, err = statement.Exec(post.UUID, post.Author, post.VoteCount, post.Title, post.URL, post.CreatedAt)
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to insert post: %v", err), "db/db.go", "")
		return err
	}

	logger.Log("info", fmt.Sprintf("Successfully inserted post: %v", post), "db/db.go", "")

	return nil
}

func DeletePost(db *sql.DB, postUUID string) error {
	query := "DELETE FROM posts WHERE uuid = ?"
	_, err := db.Exec(query, postUUID)
	return err
}

func GetPost(db *sql.DB, postUUID string) (*Post, error) {
	query := "SELECT uuid, author, votecount, title, url, createdat FROM posts WHERE uuid = ?"
	row := db.QueryRow(query, postUUID)

	var post Post
	err := row.Scan(&post.UUID, &post.Author, &post.VoteCount, &post.Title, &post.URL, &post.CreatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			// No such post exists
			return nil, nil
		} else {
			return nil, err
		}
	}

	return &post, nil
}

func UpdateVoteCount(db *sql.DB, postUUID string, increment int) error {
	query := "UPDATE posts SET votecount = votecount + ? WHERE uuid = ?"
	_, err := db.Exec(query, increment, postUUID)
	return err
}
