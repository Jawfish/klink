FROM klink:base

WORKDIR /app

COPY . /app

RUN poetry install --only main

CMD ["poetry", "run", "service"]