package db

import (
	"database/sql"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func setupDatabase(t *testing.T) *sql.DB {
	db := OpenDatabase(":memory:")
	require.NotNil(t, db)
	StartDatabase(db)
	return db
}

func Test_valid_post_insertion_succeeds(t *testing.T) {
	db := setupDatabase(t)

	post := Post{
		UUID:      "1234",
		VoteCount: 100,
		Title:     "Test Post",
		URL:       "https://test.com",
	}

	err := InsertPost(db, post)
	require.Nil(t, err)
}

func Test_duplicate_post_insertion_fails(t *testing.T) {
	db := setupDatabase(t)

	post := Post{
		UUID:      "1234",
		VoteCount: 100,
		Title:     "Test Post",
		URL:       "https://test.com",
	}

	err := InsertPost(db, post)
	require.Nil(t, err)

	err = InsertPost(db, post)
	require.NotNil(t, err)
}

func Test_post_insertion_with_nil_database_returns_error(t *testing.T) {
	post := Post{
		UUID:      "1234",
		VoteCount: 100,
		Title:     "Test Post",
		URL:       "https://test.com",
	}

	err := InsertPost(nil, post)
	require.NotNil(t, err)
}

func Test_post_insertion_verifies_correctly(t *testing.T) {
	db := setupDatabase(t)

	post := Post{
		UUID:      "1234",
		VoteCount: 100,
		Title:     "Test Post",
		URL:       "https://test.com",
	}

	err := InsertPost(db, post)
	require.Nil(t, err)

	row := db.QueryRow("SELECT uuid, votecount, title, url FROM posts WHERE uuid = ?", post.UUID)

	var queriedPost Post
	err = row.Scan(&queriedPost.UUID, &queriedPost.VoteCount, &queriedPost.Title, &queriedPost.URL)
	require.Nil(t, err)

	assert.Equal(t, post, queriedPost)
}

func Test_deletion_of_non_existent_post_returns_no_error(t *testing.T) {
	db := setupDatabase(t)

	err := DeletePost(db, "non-existent")
	require.Nil(t, err)
}

func Test_deletion_of_existing_post_succeeds(t *testing.T) {
	db := setupDatabase(t)

	post := Post{
		UUID:      "1234",
		VoteCount: 100,
		Title:     "Test Post",
		URL:       "https://test.com",
	}

	err := InsertPost(db, post)
	require.Nil(t, err)

	err = DeletePost(db, post.UUID)
	require.Nil(t, err)
}

func Test_retrieval_of_non_existent_post_returns_nil(t *testing.T) {
	db := setupDatabase(t)

	post, err := GetPost(db, "non-existent")
	require.Nil(t, err)
	require.Nil(t, post)
}

func Test_retrieval_of_existing_post_succeeds(t *testing.T) {
	db := setupDatabase(t)

	post := Post{
		UUID:      "1234",
		VoteCount: 100,
		Title:     "Test Post",
		URL:       "https://test.com",
	}

	err := InsertPost(db, post)
	require.Nil(t, err)

	queriedPost, err := GetPost(db, post.UUID)
	require.Nil(t, err)
	require.NotNil(t, queriedPost)

	assert.Equal(t, post, *queriedPost)
}

func Test_updating_vote_count_of_non_existent_post_returns_no_error(t *testing.T) {
	db := setupDatabase(t)

	err := UpdateVoteCount(db, "non-existent", 1)
	require.Nil(t, err)
}

func Test_updating_vote_count_of_existent_post_succeeds(t *testing.T) {
	db := setupDatabase(t)

	post := Post{
		UUID:      "1234",
		VoteCount: 100,
		Title:     "Test Post",
		URL:       "https://test.com",
	}

	err := InsertPost(db, post)
	require.Nil(t, err)

	err = UpdateVoteCount(db, post.UUID, 1)
	require.Nil(t, err)

	queriedPost, err := GetPost(db, post.UUID)
	require.Nil(t, err)
	require.NotNil(t, queriedPost)

	assert.Equal(t, post.VoteCount+1, queriedPost.VoteCount)
}

func Test_updating_vote_count_with_negative_increment_succeds(t *testing.T) {
	db := setupDatabase(t)

	post := Post{
		UUID:      "1234",
		VoteCount: 100,
		Title:     "Test Post",
		URL:       "https://test.com",
	}

	err := InsertPost(db, post)
	require.Nil(t, err)

	err = UpdateVoteCount(db, post.UUID, -1)
	require.Nil(t, err)

	queriedPost, err := GetPost(db, post.UUID)
	require.Nil(t, err)
	require.NotNil(t, queriedPost)

	assert.Equal(t, post.VoteCount-1, queriedPost.VoteCount)
}
