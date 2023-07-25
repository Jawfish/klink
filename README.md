# Klink

Klink is a bookmark-sharing and link aggregation platform where users can post, vote, and tag links, as well as sort and filter through these posts.

## About    

This project was created as a learning experience to further develop and practice my understanding of microservices. While I took efforts to adhere to best practices, there are likely areas where things could be improved.

The project exists as a monorepo for the sake of simplicity, but (per the microservice architecture) each service is sufficiently independent that it could be extracted into its own repository. Similarly, there is unifying top-level Docker compose file that orchestrates the deployment of all services. In a real-world production environment, each service would likely be deployed independently (usually orchestrated through something like Kubernetes) and they have been designed in such a way that this would be possible.


## Architecture

Klink is designed with a microservice architecture in mind. The project is divided into separate services, each responsible for a specific functionality of the application. These services include:

* **Frontend (React/Next.js)**: Serves the frontend of the application.
* **User Service (FastAPI & SQLAlchemy + PostgreSQL)**: Handles CRUD operations related to users.
* **Auth Service (FastAPI)**: Handles user authentication, authorization, and identification via JWT issuance and validation.
* **Post Service (Go + SQLite)**: Handles CRUD operations related to posts.
* **Gateway Service (Go)**: Serves as the main entry point for the application. It is responsible for routing client requests to the appropriate service.
* **Message Broker (RabbitMQ)**: Used for asynchronous communication between services.
* **Tests (Postman)**: A collection of Postman tests used for E2E and integration testing.
* **Fluentd + Elasticsearch + Kibana**: Used for logging and monitoring.


## Deployment

TODO


## License

This project is open source under the MIT license.
