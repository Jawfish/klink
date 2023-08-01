package api

type Post struct {
	PostUUID    string `json:"post_uuid"`
	CreatorUUID string `json:"creator_uuid"`
	VoteCount   int    `json:"voteCount"`
	Title       string `json:"title"`
	URL         string `json:"url"`
	CreatedAt   string `json:"createdAt"`
}
