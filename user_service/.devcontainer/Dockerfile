FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

ENV PYTHONUNBUFFERED 1

# Install PostgreSQL for pytest-postgresql
RUN apt-get update && apt-get install -y postgresql postgresql-contrib