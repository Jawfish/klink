package utils

import "service/logger"

func FailOnError(err error, msg string) {
	if err != nil {
		logger.Log(logger.Error, msg, "utils/utils.go", "")
	}
}
