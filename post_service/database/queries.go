package database

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
	statement, err := db.Prepare("INSERT INTO posts (post_uuid, creator_uuid, votecount, title, url, createdat) VALUES (?, ?, ?, ?, ?, ?)")
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to prepare statement: %v", err), "db/db.go", "")
		return err
	}

	_, err = statement.Exec(post.PostUUID, post.CreatorUUID, post.VoteCount, post.Title, post.URL, post.CreatedAt)
	if err != nil {
		logger.Log("error", fmt.Sprintf("Failed to insert post: %v", err), "db/db.go", "")
		return err
	}

	logger.Log("info", fmt.Sprintf("Successfully inserted post: %v", post), "db/db.go", "")

	return nil
}

func DeletePost(db *sql.DB, postUUID string) error {
	query := "DELETE FROM posts WHERE post_uuid = ?"
	_, err := db.Exec(query, postUUID)
	return err
}

func GetPost(db *sql.DB, postUUID string) (*Post, error) {
	query := "SELECT post_uuid, creator_uuid, votecount, title, url, createdat FROM posts WHERE post_uuid = ?"
	row := db.QueryRow(query, postUUID)

	var post Post
	err := row.Scan(&post.PostUUID, &post.CreatorUUID, &post.VoteCount, &post.Title, &post.URL, &post.CreatedAt)
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

func GetPosts(db *sql.DB, offset int, limit int) ([]Post, error) {
	query := "SELECT post_uuid, creator_uuid, votecount, title, url, createdat FROM posts ORDER BY createdat DESC LIMIT ? OFFSET ?"
	rows, err := db.Query(query, limit, offset)

	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var posts []Post
	for rows.Next() {
		var post Post
		if err := rows.Scan(&post.PostUUID, &post.CreatorUUID, &post.VoteCount, &post.Title, &post.URL, &post.CreatedAt); err != nil {
			return nil, err
		}
		posts = append(posts, post)
	}

	return posts, nil
}

func UpdateVoteCount(db *sql.DB, postUUID string, increment int) error {
	query := "UPDATE posts SET votecount = votecount + ? WHERE post_uuid = ?"
	_, err := db.Exec(query, increment, postUUID)
	return err
}
