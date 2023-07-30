package rabbitmq

import (
	"database/sql"
	"fmt"
	"testing"

	database "service/db"
)

func setupDB() (*sql.DB, error) {
	db := database.OpenDatabase(":memory:")
	if db == nil {
		return nil, fmt.Errorf("Failed to open in-memory DB")
	}

	database.StartDatabase(db)
	return db, nil
}

func TestHandleVote(t *testing.T) {
	db, err := setupDB()
	if err != nil {
		t.Fatalf("Failed to setup in-memory DB: %v", err)
	}
	defer db.Close()

	tests := []struct {
		name    string
		event   VoteEvent
		wantErr bool
	}{
		{
			name: "Upvote should update vote count",
			event: VoteEvent{
				PostUUID:  "test-post",
				VoterUUID: "test-voter",
				Type:      Upvote,
			},
			wantErr: false,
		},
		{
			name: "Downvote should update vote count",
			event: VoteEvent{
				PostUUID:  "test-post",
				VoterUUID: "test-voter",
				Type:      Downvote,
			},
			wantErr: false,
		},
		{
			name: "Invalid vote type should return error",
			event: VoteEvent{
				PostUUID:  "test-post",
				VoterUUID: "test-voter",
				Type:      "invalid",
			},
			wantErr: true,
		},
		{
			name: "Empty voter UUID should return error",
			event: VoteEvent{
				PostUUID:  "test-post",
				VoterUUID: "",
				Type:      Upvote,
			},
			wantErr: true,
		},
		{
			name: "Empty post UUID should return error",
			event: VoteEvent{
				PostUUID:  "",
				VoterUUID: "test-voter",
				Type:      Upvote,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := HandleVote(db, tt.event)
			if (err != nil) != tt.wantErr {
				t.Errorf("HandleVote() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestHandlePost(t *testing.T) {
	db, err := setupDB()
	if err != nil {
		t.Fatalf("Failed to setup in-memory DB: %v", err)
	}
	defer db.Close()

	tests := []struct {
		name    string
		event   PostEvent
		wantErr bool
	}{
		{
			name: "HandlePost should insert post",
			event: PostEvent{
				UUID:  "test-post",
				Title: "test title",
				URL:   "test-url",
				Type:  LinkPost,
			},
			wantErr: false,
		},
		{
			name: "Empty post UUID should return error",
			event: PostEvent{
				UUID:  "",
				Title: "test title",
				URL:   "test-url",
				Type:  LinkPost,
			},
			wantErr: true,
		},
		{
			name: "Empty post title should return error",
			event: PostEvent{
				UUID:  "test-post",
				Title: "",
				URL:   "test-url",
				Type:  LinkPost,
			},
			wantErr: true,
		},
		{
			name: "Empty post URL should return error",
			event: PostEvent{
				UUID:  "test-post",
				Title: "test title",
				URL:   "",
				Type:  LinkPost,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := HandlePost(db, tt.event)
			if (err != nil) != tt.wantErr {
				t.Errorf("HandlePost() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
