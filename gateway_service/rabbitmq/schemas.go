package rabbitmq

type VoteType string

const (
	Upvote   VoteType = "upvote"
	Downvote VoteType = "downvote"
)

type VoteEvent struct {
	PostUUID  string   `json:"post_uuid"`
	VoterUUID string   `json:"voter_uuid"`
	Type      VoteType `json:"type"`
}

type PostType string

const (
	LinkPost PostType = "link"
)

type PostEvent struct {
	Type        PostType `json:"type"`
	CreatorUUID string   `json:"creator_uuid"`
	Title       string   `json:"title"`
	URL         string   `json:"url"`
}
