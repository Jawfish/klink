#!/bin/bash

docker build --no-cache . -t klink:base
docker build --no-cache -t klink:user_service -f user_service/Dockerfile user_service
docker build --no-cache -t klink:auth_service -f auth_service/Dockerfile auth_service