package database

type Vote struct {
	ID        int
	PostUUID  string
	VoterUUID string
	IsUpvote  bool
}

type Post struct {
	PostUUID    string
	CreatorUUID string
	VoteCount   int
	Title       string
	URL         string
	CreatedAt   string
}
