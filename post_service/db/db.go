package db

import (
	"database/sql"
	"fmt"
	"service/logger"

	_ "github.com/mattn/go-sqlite3"
)

func StartDatabase(db *sql.DB) {
	logger.Log("info", "Creating posts table...", "db/db.go", "")
	statement, err := db.Prepare("CREATE TABLE IF NOT EXISTS posts (uuid TEXT PRIMARY KEY, author TEXT, votecount INTEGER, title TEXT, url TEXT, createdat TEXT)")
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to prepare statement: %v", err), "db/db.go", "")
	}
	_, err = statement.Exec()
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to create table: %v", err), "db/db.go", "")
	}
	logger.Log("info", "Posts table created successfully.", "db/db.go", "")
}

func OpenDatabase(path string) *sql.DB {
	logger.Log("info", fmt.Sprintf("Opening SQLite database at %s...", path), "db/db.go", "")
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to open database: %v", err), "db/db.go", "")
		return nil
	}

	// Execute a simple query to check the database is accessible
	_, err = db.Exec("SELECT 1")
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to open database: %v", err), "db/db.go", "")
		return nil
	}

	logger.Log("info", fmt.Sprintf("Successfully opened SQLite database at %s.", path), "db/db.go", "")
	return db
}
