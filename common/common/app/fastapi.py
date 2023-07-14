import logging
from contextlib import ContextDecorator, contextmanager
from importlib.resources import path

from fastapi import APIRouter, FastAPI
from uvicorn import Config, Server

from common.api.exceptions.exception_handlers import handle_managed_exception
from common.api.exceptions.managed_exception import ManagedException
from common.service_logging import configure_logging, load_config_file


class ServiceSetupError(Exception):
    """Exception raised when the service setup fails."""


class FastAPIServer:
    LOG_CONFIG_PATH = "common.config"
    LOG_CONFIG_FILE = "logging.json"

    def __init__(self, router: APIRouter, host: str, port: int) -> None:
        self.router = router
        self.host = host
        self.port = port
        self.app = FastAPI()
        self.server = None
        self.log_config_file = self._get_log_config_file()

        self._setup()

    def _get_log_config_file(self) -> str:
        with path(
            self.LOG_CONFIG_PATH,
            self.LOG_CONFIG_FILE,
        ) as p:
            return str(p)

    @contextmanager
    def _setup_logging(self) -> ContextDecorator:
        try:
            log_config = load_config_file(self.log_config_file)
            configure_logging(log_config)
            yield
        except FileNotFoundError as e:
            msg = "Configuration file not found"
            raise ServiceSetupError(msg) from e

    def _setup(self) -> None:
        with self._setup_logging():
            self.app.include_router(self.router)
            self.app.add_exception_handler(ManagedException, handle_managed_exception)

    def run(self) -> None:
        logging.info("Starting service at http://%s:%s", self.host, self.port)
        logging.info("Swagger UI is at http://%s:%s/docs", self.host, self.port)

        self.server = Server(
            Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_config=self.log_config_file,
            ),
        )

        self.server.run()
