package rabbitmq

import (
	"testing"

	"service/database"

	"github.com/google/uuid"
)

func Test_vote_events_are_handled_as_expected(t *testing.T) {
	db := database.SetupTestDB(t)

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

func Test_post_events_are_handled_as_expected(t *testing.T) {
	db := database.SetupTestDB(t)

	tests := []struct {
		name    string
		event   PostEvent
		wantErr bool
	}{
		{
			name: "HandlePost should insert post",
			event: PostEvent{
				Title:       "test title",
				CreatorUUID: uuid.New().String(),
				URL:         "test-url",
			},
			wantErr: false,
		},
		{
			name: "Empty creator UUID should return error",
			event: PostEvent{
				Title:       "test title",
				CreatorUUID: "",
				URL:         "test-url",
			},
			wantErr: true,
		},
		{
			name: "Empty post title should return error",
			event: PostEvent{
				Title:       "",
				CreatorUUID: uuid.New().String(),
				URL:         "test-url",
			},
			wantErr: true,
		},
		{
			name: "Empty post URL should return error",
			event: PostEvent{
				Title:       "test title",
				CreatorUUID: uuid.New().String(),
				URL:         "",
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
