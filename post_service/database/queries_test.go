package database

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func Test_valid_post_insertion_succeeds(t *testing.T) {
	db := SetupTestDB(t)

	post := GenerateTestPost()

	err := InsertPost(db, post)
	require.Nil(t, err)
}

func Test_duplicate_post_insertion_fails(t *testing.T) {
	db := SetupTestDB(t)

	post := GenerateTestPost()

	err := InsertPost(db, post)
	require.Nil(t, err)

	err = InsertPost(db, post)
	require.NotNil(t, err)
}

func Test_post_insertion_with_nil_database_returns_error(t *testing.T) {
	post := GenerateTestPost()

	err := InsertPost(nil, post)
	require.NotNil(t, err)
}

func Test_post_insertion_verifies_correctly(t *testing.T) {
	db := SetupTestDB(t)

	post := GenerateTestPost()

	err := InsertPost(db, post)
	require.Nil(t, err)

	row := db.QueryRow("SELECT uuid, author, votecount, title, url, createdat FROM posts WHERE uuid = ?", post.UUID)

	var queriedPost Post
	err = row.Scan(&queriedPost.UUID, &queriedPost.Author, &queriedPost.VoteCount, &queriedPost.Title, &queriedPost.URL, &queriedPost.CreatedAt)
	require.Nil(t, err)

	assert.Equal(t, post, queriedPost)
}

func Test_deletion_of_non_existent_post_returns_no_error(t *testing.T) {
	db := SetupTestDB(t)

	err := DeletePost(db, "non-existent")
	require.Nil(t, err)
}

func Test_deletion_of_existing_post_succeeds(t *testing.T) {
	db := SetupTestDB(t)

	post := GenerateTestPost()

	err := InsertPost(db, post)
	require.Nil(t, err)

	err = DeletePost(db, post.UUID)
	require.Nil(t, err)
}

func Test_retrieval_of_non_existent_post_returns_nil(t *testing.T) {
	db := SetupTestDB(t)

	post, err := GetPost(db, "non-existent")
	require.Nil(t, err)
	require.Nil(t, post)
}

func Test_retrieval_of_existing_post_succeeds(t *testing.T) {
	db := SetupTestDB(t)

	post := GenerateTestPost()

	err := InsertPost(db, post)
	require.Nil(t, err)

	queriedPost, err := GetPost(db, post.UUID)
	require.Nil(t, err)
	require.NotNil(t, queriedPost)

	assert.Equal(t, post, *queriedPost)
}

func Test_paginated_retrieval_of_posts_succeeds(t *testing.T) {
	db := SetupTestDB(t)

	var posts []Post
	numPosts := 4

	for i := 0; i < numPosts; i++ {
		post := GenerateTestPost()
		post.CreatedAt = time.Now().Add(-1 * time.Duration(i) * time.Hour).Format(time.RFC3339)
		posts = append(posts, post)

		err := InsertPost(db, post)
		require.Nil(t, err)
	}

	queriedPosts, err := GetPosts(db, 0, 2)
	require.Nil(t, err)
	require.NotNil(t, queriedPosts)

	// Expect the newest posts to be returned first
	assert.Equal(t, posts[0].UUID, queriedPosts[0].UUID)
	assert.Equal(t, posts[1].UUID, queriedPosts[1].UUID)

	queriedPosts, err = GetPosts(db, 2, 2)
	require.Nil(t, err)
	require.NotNil(t, queriedPosts)

	// // The second page should start with the second oldest post
	assert.Equal(t, posts[2].UUID, queriedPosts[0].UUID)
	assert.Equal(t, posts[3].UUID, queriedPosts[1].UUID)
}

func Test_updating_vote_count_of_non_existent_post_returns_no_error(t *testing.T) {
	db := SetupTestDB(t)

	err := UpdateVoteCount(db, "non-existent", 1)
	require.Nil(t, err)
}

func Test_updating_vote_count_of_existent_post_succeeds(t *testing.T) {
	db := SetupTestDB(t)

	post := GenerateTestPost()

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
	db := SetupTestDB(t)

	post := GenerateTestPost()

	err := InsertPost(db, post)
	require.Nil(t, err)

	err = UpdateVoteCount(db, post.UUID, -1)
	require.Nil(t, err)

	queriedPost, err := GetPost(db, post.UUID)
	require.Nil(t, err)
	require.NotNil(t, queriedPost)

	assert.Equal(t, post.VoteCount-1, queriedPost.VoteCount)
}
