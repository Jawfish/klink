package api

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"strconv"

	"service/database"
	"service/logger"
)

const defaultPageSize = 10

func getPosts(db *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		page, _ := strconv.Atoi(r.URL.Query().Get("page"))
		if page < 1 {
			page = 1
		}

		dbPosts, err := database.GetPosts(db, (page-1)*defaultPageSize, defaultPageSize)
		if err != nil {
			logger.Log("error", err.Error(), "api/api.go", "getPosts")
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		var posts []Post
		for _, dbPost := range dbPosts {
			post := Post{
				PostUUID:    dbPost.PostUUID,
				CreatorUUID: dbPost.CreatorUUID,
				VoteCount:   dbPost.VoteCount,
				Title:       dbPost.Title,
				URL:         dbPost.URL,
				CreatedAt:   dbPost.CreatedAt,
			}
			posts = append(posts, post)
		}

		json.NewEncoder(w).Encode(posts)
	}
}

func SetupRoutes(db *sql.DB) {
	http.HandleFunc("/posts", getPosts(db))
}
