package api

type Post struct {
	PostUUID    string `json:"post_uuid"`
	CreatorUUID string `json:"creator_uuid"`
	VoteCount   int    `json:"vote_count"`
	Title       string `json:"title"`
	URL         string `json:"url"`
	CreatedAt   string `json:"created_at"`
}
