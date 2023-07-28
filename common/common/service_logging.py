import logging
import os

from dotenv import load_dotenv

load_dotenv()

FLUENTD_HOST = os.getenv("FLUENTD_HOST", "localhost")
FLUENTD_PORT = int(os.getenv("FLUENTD_PORT", "24224"))
LOG_FILE_PATH = os.getenv("LOG_FILENAME", "logs/service.log")
LOG_TO_STDOUT = os.getenv("LOG_TO_STDOUT", "False").lower() == "true"

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "file": {
            "datefmt": "%Y-%m-%dT%H:%M:%S",
            "format": "%(asctime)s | %(levelname)-8s | %(message)s",
        },
        "fluent": {
            "()": "fluent.handler.FluentRecordFormatter",
            "format": {
                "host": "%(hostname)s",
                "level": "%(levelname)s",
                "message": "%(message)s",
                "stack_trace": "%(exc_text)s",
                "where": "%(module)s.%(funcName)s:%(lineno)d",
            },
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_FILE_PATH,
            "formatter": "file",
            "when": "midnight",
        },
        "fluent": {
            "class": "fluent.handler.FluentHandler",
            "formatter": "fluent",
            "host": FLUENTD_HOST,
            "port": FLUENTD_PORT,
            "tag": "service",
        },
    },
    "root": {
        "handlers": [
            "fluent",
            "file",
        ],
        "level": "INFO",
    },
}

if LOG_TO_STDOUT:
    LOGGING_CONFIG["handlers"]["console"] = {
        "class": "logging.StreamHandler",
        "formatter": "file",
    }
    LOGGING_CONFIG["root"]["handlers"].append("console")

def _ensure_dir_exists(path: str) -> None:
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)


def configure_logging() -> None:
    _ensure_dir_exists(LOG_FILE_PATH)
    logging.config.dictConfig(LOGGING_CONFIG)
