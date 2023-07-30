package api

type Post struct {
	UUID      string `json:"uuid"`
	Author    string `json:"author"`
	VoteCount int    `json:"voteCount"`
	Title     string `json:"title"`
	URL       string `json:"url"`
	CreatedAt string `json:"createdAt"`
}
