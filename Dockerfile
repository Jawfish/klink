FROM python:3.11.4-slim

# Install dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev

# Install Poetry
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false

# Install the common package
COPY common /common
WORKDIR /common
RUN poetry install
