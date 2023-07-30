package db

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_database_opens_with_valid_path(t *testing.T) {
	db := OpenDatabase(":memory:")
	require.NotNil(t, db)
}

func Test_database_fails_to_open_with_invalid_path(t *testing.T) {
	db := OpenDatabase("/invalid/path")
	require.Nil(t, db)
}

func Test_valid_database_starts(t *testing.T) {
	db := OpenDatabase(":memory:")
	require.NotNil(t, db)
	StartDatabase(db)
}

func Test_database_restarts_without_error(t *testing.T) {
	db := OpenDatabase(":memory:")
	require.NotNil(t, db)
	StartDatabase(db)
	StartDatabase(db)
}
