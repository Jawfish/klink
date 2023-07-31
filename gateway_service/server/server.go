package server

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"service/rabbitmq"

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

func handleGetPosts(c *gin.Context) {
	proxyRequest(c, os.Getenv("POST_SERVICE_HOST"), os.Getenv("POST_SERVICE_PORT"))
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

func Run() {
	if err := SetupRabbitMQ(); err != nil {
		log.Fatal(err)
	}
	r := gin.Default()
	r.POST("/posts", handleCreatePost)
	r.PATCH("/posts/:post_id", handleVote)
	r.GET("/posts", handleGetPosts)
	r.POST("/auth/register", handleAuth)
	r.POST("/auth/token", handleAuth)
	r.Run(os.Getenv("HOST_IP") + ":" + os.Getenv("HOST_PORT"))
}
