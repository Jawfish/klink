package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strconv"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"service/database"
)

func Test_posts_can_be_retrieved_in_paginated_manner(t *testing.T) {
	db := database.SetupTestDB(t)

	// Insert dummy data
	for i := 1; i <= 25; i++ {
		post := database.Post{
			UUID:      "test-post-" + strconv.Itoa(i),
			Author:    "test-author",
			VoteCount: i,
			Title:     "test title " + strconv.Itoa(i),
			URL:       "test-url-" + strconv.Itoa(i),
			CreatedAt: time.Now().Add(-time.Duration(i) * time.Minute).Format(time.RFC3339),
		}
		err := database.InsertPost(db, post)
		require.NoError(t, err)
	}

	// Test that each page consists of the expected posts
	testPage := func(pageNum int, expectedLen int, expectedFirstUUID string, expectedLastUUID string) {
		req, err := http.NewRequest("GET", fmt.Sprintf("/posts?page=%d", pageNum), nil)
		require.NoError(t, err)

		rr := httptest.NewRecorder()
		handler := http.HandlerFunc(getPosts(db))
		handler.ServeHTTP(rr, req)

		assert.Equal(t, http.StatusOK, rr.Code)

		var posts []database.Post
		err = json.NewDecoder(rr.Body).Decode(&posts)
		require.NoError(t, err)
		assert.Len(t, posts, expectedLen)
		assert.Equal(t, expectedFirstUUID, posts[0].UUID)
		assert.Equal(t, expectedLastUUID, posts[len(posts)-1].UUID)
	}

	testPage(1, defaultPageSize, "test-post-1", "test-post-10")
	testPage(2, defaultPageSize, "test-post-11", "test-post-20")
	testPage(3, 5, "test-post-21", "test-post-25")
}

func Test_response_conforms_to_expected_schema(t *testing.T) {
	db := database.SetupTestDB(t)

	now := time.Now().Format(time.RFC3339)

	// Insert a dummy post
	post := database.Post{
		UUID:      "test-post",
		Author:    "test-author",
		VoteCount: 1,
		Title:     "test title",
		URL:       "test-url",
		CreatedAt: now,
	}
	err := database.InsertPost(db, post)
	require.NoError(t, err)

	req, err := http.NewRequest("GET", "/posts?page=1", nil)
	require.NoError(t, err)

	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(getPosts(db))
	handler.ServeHTTP(rr, req)

	assert.Equal(t, http.StatusOK, rr.Code)

	var posts []Post
	err = json.NewDecoder(rr.Body).Decode(&posts)
	require.NoError(t, err)

	// Check that the response conforms to the expected schema
	require.Len(t, posts, 1)
	assert.Equal(t, "test-post", posts[0].UUID)
	assert.Equal(t, "test-author", posts[0].Author)
	assert.Equal(t, 1, posts[0].VoteCount)
	assert.Equal(t, "test title", posts[0].Title)
	assert.Equal(t, "test-url", posts[0].URL)
	assert.Equal(t, now, posts[0].CreatedAt)
}
