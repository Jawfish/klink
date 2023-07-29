package db

import (
	"database/sql"
	"fmt"
	"service/logger"

	_ "github.com/mattn/go-sqlite3"
)

type Post struct {
	UUID      string
	VoteCount int
	Title     string
	URL       string
}

func StartDatabase(db *sql.DB) {
	logger.Log("info", "Creating posts table...", "db/db.go", "")
	statement, err := db.Prepare("CREATE TABLE IF NOT EXISTS posts (uuid TEXT PRIMARY KEY, votecount INTEGER, title TEXT, url TEXT)")
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to prepare statement: %v", err), "db/db.go", "")
	}
	_, err = statement.Exec()
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to create table: %v", err), "db/db.go", "")
	}
	logger.Log("info", "Posts table created successfully.", "db/db.go", "")
}

func InsertPost(db *sql.DB, post Post) {
	logger.Log("info", fmt.Sprintf("Inserting post: %v", post), "db/db.go", "")
	statement, err := db.Prepare("INSERT INTO posts (uuid, votecount, title, url) VALUES (?, ?, ?, ?)")
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to prepare statement: %v", err), "db/db.go", "")
	}
	_, err = statement.Exec(post.UUID, post.VoteCount, post.Title, post.URL)
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to insert post: %v", err), "db/db.go", "")
	}
	logger.Log("info", fmt.Sprintf("Successfully inserted post: %v", post), "db/db.go", "")
}

func OpenDatabase(path string) *sql.DB {
	logger.Log("info", fmt.Sprintf("Opening SQLite database at %s...", path), "db/db.go", "")
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to open database: %v", err), "db/db.go", "")
	}
	logger.Log("info", fmt.Sprintf("Successfully opened SQLite database at %s.", path), "db/db.go", "")
	return db
}
