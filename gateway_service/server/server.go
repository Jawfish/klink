package server

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"service/rabbitmq"
	"strings"

	"github.com/gin-gonic/gin"
)

type Env struct {
	RabbitMQ *rabbitmq.RabbitMQ
}

var env *Env

func SetupRabbitMQ() error {
	var err error
	env = &Env{}
	env.RabbitMQ, err = rabbitmq.NewRabbitMQ()
	return err
}
func proxyRequest(c *gin.Context, serviceHost string, servicePort string) {
	client := &http.Client{}

	req, err := http.NewRequest(c.Request.Method, "http://"+serviceHost+":"+servicePort+c.Request.RequestURI, c.Request.Body)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}

	for name, headers := range c.Request.Header {
		for _, h := range headers {
			req.Header.Add(name, h)
		}
	}

	resp, err := client.Do(req)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	defer resp.Body.Close()

	c.DataFromReader(resp.StatusCode, resp.ContentLength, resp.Header.Get("Content-Type"), resp.Body, nil)
}

func handleAuth(c *gin.Context) {
	proxyRequest(c, os.Getenv("AUTH_SERVICE_HOST"), os.Getenv("AUTH_SERVICE_PORT"))
}

func getUsername(serviceHost string, servicePort string, uuid string) (string, error) {
	type UsernameIn struct {
		Username string `json:"username"`
	}

	client := &http.Client{}
	url := "http://" + serviceHost + ":" + servicePort + "/users/" + uuid
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", err
	}

	log.Println("URL: ", url)
	log.Println("UUID: ", uuid)

	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	bodyBytes, _ := io.ReadAll(resp.Body)
	bodyString := string(bodyBytes)
	log.Println("Response Body: ", bodyString)

	var user UsernameIn
	err = json.NewDecoder(strings.NewReader(bodyString)).Decode(&user)
	if err != nil {
		return "", err
	}

	return user.Username, nil
}

func getPosts(postServiceHost string, postServicePort string, userServiceHost string, userServicePort string) ([]PostOut, error) {
	client := &http.Client{}
	req, err := http.NewRequest("GET", "http://"+postServiceHost+":"+postServicePort+"/posts", nil)
	if err != nil {
		return nil, err
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	type PostIn struct {
		PostUUID    string `json:"post_uuid"`
		CreatorUUID string `json:"creator_uuid"`
		VoteCount   int    `json:"vote_count"`
		Title       string `json:"title"`
		URL         string `json:"url"`
		CreatedAt   string `json:"created_at"`
	}

	var postResponses []PostIn
	err = json.NewDecoder(resp.Body).Decode(&postResponses)
	if err != nil {
		return nil, err
	}

	var posts []PostOut
	for _, postResponse := range postResponses {
		// sub-optimal, because a request is made for each post
		username, err := getUsername(userServiceHost, userServicePort, postResponse.CreatorUUID)
		if err != nil {
			return nil, err
		}

		post := PostOut{
			PostUUID:  postResponse.PostUUID,
			Author:    username,
			VoteCount: postResponse.VoteCount,
			Title:     postResponse.Title,
			URL:       postResponse.URL,
			CreatedAt: postResponse.CreatedAt,
		}

		posts = append(posts, post)
	}

	return posts, nil
}

func handleGetPosts(c *gin.Context) {
	posts, err := getPosts(os.Getenv("POST_SERVICE_HOST"), os.Getenv("POST_SERVICE_PORT"), os.Getenv("USER_SERVICE_HOST"), os.Getenv("USER_SERVICE_PORT"))
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}

	c.JSON(200, posts)
}

func handleCreatePost(c *gin.Context) {
	queueName := os.Getenv("RABBITMQ_POST_SERVICE_QUEUE")
	var jsonMessage gin.H
	if err := c.BindJSON(&jsonMessage); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	messageBytes, err := json.Marshal(jsonMessage)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	err = env.RabbitMQ.SendToQueue(queueName, string(messageBytes))
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	c.JSON(200, gin.H{
		"message": "post creation in progress",
	})
}

func handleVote(c *gin.Context) {
	queueName := os.Getenv("RABBITMQ_POST_SERVICE_QUEUE")
	postID := c.Param("post_id")

	var voteEvent rabbitmq.VoteEvent
	if err := c.ShouldBindJSON(&voteEvent); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if voteEvent.PostUUID != postID {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Mismatched post_id"})
		return
	}

	messageBytes, err := json.Marshal(voteEvent)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	err = env.RabbitMQ.SendToQueue(queueName, string(messageBytes))
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	c.JSON(200, gin.H{
		"message": "vote processed",
	})
}

func jwtAuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := c.GetHeader("Authorization")
		if token == "" {
			c.AbortWithStatusJSON(401, gin.H{"error": "No Authorization header provided"})
			return
		}

		serviceHost := os.Getenv("AUTH_SERVICE_HOST")
		servicePort := os.Getenv("AUTH_SERVICE_PORT")
		client := &http.Client{}
		req, err := http.NewRequest("GET", "http://"+serviceHost+":"+servicePort+"/user-identity", nil)

		if err != nil {
			c.AbortWithStatusJSON(500, gin.H{"error": "Could not validate token"})
			return
		}

		req.Header.Add("Authorization", token)

		resp, err := client.Do(req)
		if err != nil || resp.StatusCode != 200 {
			c.AbortWithStatusJSON(401, gin.H{"error": "Invalid token"})
			return
		}

		c.Next()
	}
}

func Run() {
	if err := SetupRabbitMQ(); err != nil {
		log.Fatal(err)
	}
	r := gin.Default()
	r.GET("/posts", handleGetPosts)
	r.POST("/register", handleAuth)
	r.POST("/token", handleAuth)

	// require auth for all routes below
	r.Use(jwtAuthMiddleware())

	r.POST("/posts", handleCreatePost)
	r.PATCH("/posts/:post_id", handleVote)
	r.Run(os.Getenv("HOST_IP") + ":" + os.Getenv("HOST_PORT"))
}
