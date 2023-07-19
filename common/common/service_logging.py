import json
import logging
import os
from importlib.resources import path

DEFAULT_LOG_CONFIG_PATH = "common.config"
DEFAULT_LOG_CONFIG_FILE = "logging.json"


def _ensure_dir_exists(path: str) -> None:
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)


def load_default_config_file() -> dict:
    with path(
        DEFAULT_LOG_CONFIG_PATH,
        DEFAULT_LOG_CONFIG_FILE,
    ) as p:
        return load_config_file(str(p))


def load_config_file(config_file: str) -> dict:
    try:
        with open(config_file) as file:
            return json.load(file)
    except FileNotFoundError:
        logging.exception("Configuration file %s not found.", config_file)
        raise
    except json.JSONDecodeError:
        logging.exception(
            "Failed to parse JSON from configuration file %s.",
            config_file,
        )
        raise


def configure_logging(logging_config: dict) -> None:
    """
    Configures Python's standard logging module according to provided configuration.

    The configuration should be a dictionary as expected by `logging.config.dictConfig`.
    """
    if "handlers" in logging_config:
        for handler in logging_config["handlers"].values():
            if "filename" in handler:
                _ensure_dir_exists(handler["filename"])

    try:
        logging.config.dictConfig(logging_config)
    except ValueError:
        logging.exception("Invalid logging configuration.")
        raise
