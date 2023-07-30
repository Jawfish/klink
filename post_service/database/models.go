package database

type Vote struct {
	ID       int
	PostUUID string
	UserUUID string
	IsUpvote bool
}

type Post struct {
	UUID      string
	Author    string
	VoteCount int
	Title     string
	URL       string
	CreatedAt string
}
