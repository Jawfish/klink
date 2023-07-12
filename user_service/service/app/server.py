import logging
import os

from common.api.exceptions.exception_handlers import handle_managed_exception
from common.api.exceptions.managed_exception import ManagedException
from common.service_logging import configure_logging, load_config_file
from fastapi import FastAPI
from uvicorn import Config, Server

from service.app.app_factory import create_app


class ServiceSetupError(Exception):
    """Exception raised when the service setup fails."""


class ServiceRunError(Exception):
    """Exception raised when the service fails to run."""


def run(
    app: FastAPI | None,
    host: str | None,
    port: int | None,
    log_config: dict | None,
) -> Server:
    if not all([app, host, port, log_config]):
        msg = "The service cannot be started due to incomplete setup."
        logging.error(msg)
        raise ServiceSetupError(msg)

    logging.info("Starting service at http://%s:%s", host, port)
    logging.info("Swagger UI is at http://%s:%s/docs", host, port)

    try:
        server = Server(
            Config(
                app=app,
                host=host,
                port=port,
                log_config=log_config,
            ),
        )
        server.run()
    except Exception as e:
        logging.exception("An error occurred while starting the service")
        msg = "An error occurred while starting the service"
        raise ServiceRunError(msg) from e
    else:
        return server


def setup() -> tuple[FastAPI | None, str | None, int | None, dict | None]:
    try:
        log_config = load_config_file("log_config.json")
        configure_logging(log_config)

        app = create_app()
        app.add_exception_handler(ManagedException, handle_managed_exception)

        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "80"))

    except FileNotFoundError as e:
        logging.exception("Configuration file not found")
        msg = "Configuration file not found"
        raise ServiceSetupError(msg) from e
    except Exception:
        logging.exception("An error occurred while setting up the service")
        raise
    else:
        return app, host, port, log_config
