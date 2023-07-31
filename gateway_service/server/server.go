package server

import (
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

func proxyRequest(c *gin.Context, serviceHost string, servicePort string) {
	resp, err := http.Get("http://" + serviceHost + ":" + servicePort + c.Request.RequestURI)
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
	// functionality here
}

func Run() {
	r := gin.Default()
	r.POST("/posts", handleGetPosts)
	r.POST("/auth/register", handleAuth)
	r.POST("/auth/token", handleAuth)
	r.GET("/posts", handleGetPosts)
	r.Run(os.Getenv("HOST_IP") + ":" + os.Getenv("HOST_PORT"))
}
