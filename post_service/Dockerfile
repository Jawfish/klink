FROM golang:1.20.6-alpine3.18 AS build-env

RUN apk update && apk add gcc musl-dev

WORKDIR /app

# Copy project files to the working directory
COPY go.mod go.sum ./
COPY cmd .
COPY internal .

RUN go mod download

RUN CGO_ENABLED=1 GOOS=linux go build -v -a -tags netgo -ldflags '-w -extldflags "-static"' -o main .

FROM alpine:3.18

WORKDIR /app

COPY --from=build-env /app/main .

RUN addgroup -g 10001 -S appgroup && adduser -u 10001 -S appuser -G appgroup

USER appuser

CMD ["./main"]
