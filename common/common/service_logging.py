import json
import logging
import logging.config
import os


def load_config_file(config_file: str) -> dict:
    """Loads a JSON config file.

    Args:
        config_file (str): Path to the JSON config file.

    Returns:
        dict: Loaded JSON data as a dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
        json.JSONDecodeError: If the config file is not valid JSON.
    """
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
    """Configures Python's standard logging module according to provided configuration.

    The configuration should be a dictionary as expected by `logging.config.dictConfig`.

    Args:
        logging_config (dict): Logging configuration dictionary.

    Raises:
        ValueError: If the logging configuration is not valid.
    """
    if "handlers" in logging_config:
        for handler in logging_config["handlers"].values():
            if "filename" in handler:
                dir_name = os.path.dirname(handler["filename"])
                os.makedirs(dir_name, exist_ok=True)

    try:
        logging.config.dictConfig(logging_config)
    except ValueError:
        logging.exception("Invalid logging configuration.")
        raise
