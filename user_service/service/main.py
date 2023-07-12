import logging
import os

from common.service_logging import configure_logging, load_config_file
from fastapi import FastAPI
from uvicorn import Config, Server

from service.api.exception_handlers import handle_managed_exception
from service.api.exceptions import ManagedException
from service.app.app_factory import create_app


def run_server(app: FastAPI, host: str, port: int, log_config: dict) -> None:
    logging.info("Starting service at http://%s:%s", host, port)
    logging.info("Swagger UI is at http://%s:%s/docs", host, port)
    config = Config(
        app=app,
        host=host,
        port=port,
        log_config=log_config,
    )
    server = Server(config)
    server.run()


def main() -> None:
    try:
        log_config = load_config_file("log_config.json")
        configure_logging(log_config)
        app = create_app()
        app.add_exception_handler(ManagedException, handle_managed_exception)
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "80"))

        run_server(app, host, port, log_config)

    except FileNotFoundError:
        logging.exception("Configuration file not found")
    except Exception:
        logging.exception("An error occurred while starting the service")


if __name__ == "__main__":
    main()
