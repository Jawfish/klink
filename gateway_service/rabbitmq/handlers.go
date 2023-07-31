package rabbitmq

import (
	"encoding/json"
	"net/http"

	"github.com/gin-gonic/gin"
)

type Env struct {
	RabbitMQ *RabbitMQ
}

func (env *Env) HandleEvent(c *gin.Context) {
	queueName := c.Param("queueName")
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
		"message": "event published",
	})
}
