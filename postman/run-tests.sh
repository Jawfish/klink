#!/bin/sh

wait_for_service() {
    echo "Waiting for service $1 to be ready..."
    while true; do
        curl --silent $1 > /dev/null
        if [ $? -eq 0 ]; then
            echo "Service $1 is ready."
            break
        else
            echo "Service $1 cannot be reached. Retrying in 5 seconds..."
            sleep 5
        fi
    done
}

wait_for_service ${AUTH_SERVICE_URL}
wait_for_service ${USER_SERVICE_URL}

newman run collection.json \
    --env-var "AUTH_SERVICE_URL=${AUTH_SERVICE_URL}" \
    --env-var "USER_SERVICE_URL=${USER_SERVICE_URL}"
