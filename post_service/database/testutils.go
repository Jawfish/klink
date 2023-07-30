package database

import (
	"database/sql"
	"fmt"
	"math/rand"
	"testing"
	"time"
)

func SetupTestDB(t *testing.T) *sql.DB {
	db := OpenDatabase(":memory:")

	StartDatabase(db)

	t.Cleanup(func() {
		db.Close()
	})

	return db
}

func GenerateTestPost() Post {
	return Post{
		UUID:      fmt.Sprintf("%d", rand.Int()),
		Author:    "unknown",
		VoteCount: rand.Int(),
		Title:     "Test Post",
		URL:       "https://test.com",
		CreatedAt: time.Now().Format(time.RFC3339),
	}
}
