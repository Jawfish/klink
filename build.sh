#!/bin/bash

docker build . -t klink:base
docker build -t klink:user_service -f user_service/Dockerfile user_service
docker build -t klink:auth_service -f auth_service/Dockerfile auth_service