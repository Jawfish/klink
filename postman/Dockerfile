FROM node:20.5

WORKDIR /app

RUN npm install -g newman

COPY collection.json /app
COPY run-tests.sh /app

CMD ["sh", "/app/run-tests.sh"]