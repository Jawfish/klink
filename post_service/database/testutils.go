package database

import (
	"database/sql"
	"testing"

	"github.com/google/uuid"
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
		PostUUID:    uuid.New().String(),
		CreatorUUID: uuid.New().String(),
		VoteCount:   0,
		Title:       "Test Title",
		URL:         "https://test.com",
		CreatedAt:   "2023-01-01T00:00:00Z",
	}
}
