import logging
import logging.config
import os

from dotenv import load_dotenv
from fluent import handler as fluent_handler

load_dotenv()


def load_log_config() -> None:
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
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "root": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "handlers": ["fluent", "console"],
        },
    }

    logging.config.dictConfig(logging_config)
