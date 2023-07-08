import logging
import logging.config
import os

from dotenv import load_dotenv
from fluent import handler as fluent_handler

load_dotenv()


def configure_logging() -> None:
    """Loads logger configuration from environment variables.

    Environment variables used:
        LOG_TAG: The logging tag. Default is "test".
        LOG_HOST: The logging host. Default is "localhost".
        LOG_PORT: The logging port. Default is 24224.
        LOG_LEVEL: The logging level. Default is "INFO".

    Note:
        The logger configuration dictionary should be formatted according to the
        specifications found in Python's logging.config.dictConfig documentation:
        https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig
    """

    logging_config = {
        "version": 1,
        "handlers": {
            "fluent": {
                "class": "fluent.handler.FluentHandler",
                "formatter": "fluent",
                "tag": os.getenv("LOG_TAG", "test"),
                "host": os.getenv("LOG_HOST", "localhost"),
                "port": int(os.getenv("LOG_PORT", "24224")),
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
                "filename": "logs/log.log",
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
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "handlers": ["fluent", "console", "file"],
        },
    }

    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.config.dictConfig(logging_config)
