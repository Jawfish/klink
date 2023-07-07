# Klink

Klink is a social bookmark-sharing and link aggregation platform where users can post, vote, and tag links, as well as sort and filter through these posts.

## About    

This project was created as a learning experience to further develop and practice my understanding of microservices. While I took efforts to adhere to best practices, there are likely areas where things could be improved.

The project exists as a monorepo for the sake of simplicity, but (per the microservice architecture) each service is sufficiently independent that it could be extracted into its own repository. Similarly, there is unifying top-level Docker compose file that orchestrates the deployment of all services. In a real-world production environment, each service would likely be deployed independently (usually orchestrated through something like Kubernetes) and they have been designed in such a way that this would be possible.


## Architecture

Klink is designed with a microservice architecture in mind. The project is divided into separate services, each responsible for a specific functionality of the application. These services include:

* **Frontend Service**: Serves the frontend of the application.
* **User Service**: Handles user registration, authentication, and account management.
* **Post Service**: Manages all operations related to posts such as voting on, creating, updating, and deleting posts.
* **Tag Service**: Handles operations related to tags.
* **Gateway Service**: Serves as the main entry point for the application. It is responsible for routing requests to the appropriate service.

The following technologies were used to build the application:
* **FastAPI**: Used to build backend microservices.
* **Flask**: Used for building the frontend service, serving HTML templates and interacting with the FastAPI backend.
* **SQLAlchemy**: Used as the ORM for handling database operations.
* **PostgreSQL**: Used as the main relational database.



## Deployment

TODO


## License

This project is open source under the MIT license.
