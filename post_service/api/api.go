package api

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"strconv"

	"service/database"
)

const defaultPageSize = 10

func getPosts(db *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		page, _ := strconv.Atoi(r.URL.Query().Get("page"))
		if page < 1 {
			page = 1
		}

		posts, err := database.GetPosts(db, (page-1)*defaultPageSize, defaultPageSize)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		json.NewEncoder(w).Encode(posts)
	}
}

func SetupRoutes(db *sql.DB) {
	http.HandleFunc("/posts", getPosts(db))
}
