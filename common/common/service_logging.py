import logging
import logging.config
import os
from typing import NamedTuple

from fluent import handler as fluent_handler


class LoggingConfig(NamedTuple):
    service_name: str
    logger_host: str
    logger_port: int
    logging_level: int = logging.INFO
    local_log_dir: str = "logs"


def configure_logging(
    config: LoggingConfig,
) -> None:
    """Configures Python's standard logging module for the service.

    Args:
        service_name (str): The name of the service.
        logger_host (str): The host of the logger.
        logger_port (int): The port of the logger.
        logging_level (logging.Level): The logging level to use.
    """

    # https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig
    logging_config = {
        "version": 1,
        "handlers": {
            "fluent": {
                "class": "fluent.handler.FluentHandler",
                "formatter": "fluent",
                "tag": config.service_name,
                "host": config.logger_host,
                "port": config.logger_port,
            },
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "console",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "file",
                "when": "midnight",
                "filename": f"{config.local_log_dir}/{config.service_name}.log",
            },
        },
        "formatters": {
            "fluent": {
                "()": fluent_handler.FluentRecordFormatter,
                "format": {
                    "host": "%(hostname)s",
                    "where": "%(module)s.%(funcName)s",
                    "type": "%(levelname)s",
                    "stack_trace": "%(exc_text)s",
                    "message": "%(message)s",
                },
            },
            "console": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(levelname)-8s | %(asctime)s | %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "bold,red",
                    "CRITICAL": "bold,white,bg_red",
                },
            },
            "file": {
                "format": "%(levelname)-8s | %(asctime)s | %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "root": {
            "level": config.logging_level,
            "handlers": ["fluent", "console", "file"],
        },
    }

    if not os.path.exists(config.local_log_dir):
        os.makedirs(config.local_log_dir)

    logging.config.dictConfig(logging_config)
