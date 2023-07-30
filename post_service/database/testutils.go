package database

import (
	"database/sql"
	"testing"
)

func SetupTestDB(t *testing.T) *sql.DB {
	db := OpenDatabase(":memory:")

	StartDatabase(db)

	t.Cleanup(func() {
		db.Close()
	})

	return db
}
