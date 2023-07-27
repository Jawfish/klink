#!/bin/bash
docker build -t klink:base .
docker compose -f ./docker-compose.test-services.yml build
docker compose -f ./docker-compose.test-services.yml up -d

docker compose -f ./docker-compose.api-tests.yml build
docker compose -f ./docker-compose.api-tests.yml run --rm postman

docker compose -f ./docker-compose.test-services.yml down
