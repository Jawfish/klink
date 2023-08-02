package server

type PostOut struct {
	PostUUID  string `json:"post_uuid"`
	Author    string `json:"author"`
	VoteCount int    `json:"vote_count"`
	Title     string `json:"title"`
	URL       string `json:"url"`
	CreatedAt string `json:"created_at"`
}
