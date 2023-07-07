import pytest
from .service_logging import create_logger, load_log_config
import logging
from logging import config
from unittest.mock import patch


def test_create_logger_provides_valid_logger_with_default_config():
    with patch.object(config, "dictConfig") as mock_logging_config:
        logger = create_logger()
        assert isinstance(logger, logging.Logger)
        mock_logging_config.assert_called_once_with(load_log_config())


def test_create_logger_provides_valid_logger_with_valid_config():
    log_config = {
        "version": 1,
        "handlers": {
            "fluent": {
                "class": "fluent.handler.FluentHandler",
                "tag": "app",
                "host": "localhost",
                "port": 24224,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["fluent"],
        },
    }

    with patch.object(config, "dictConfig") as mock_logging_config:
        logger = create_logger(log_config)
        mock_logging_config.assert_called_once_with(log_config)

    assert isinstance(logger, logging.Logger)


def test_logger_logs_message():
    log_config = {
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }

    logger = create_logger(log_config)

    with patch.object(logger, "info") as mock_info:
        logger.info("Test log message")
        mock_info.assert_called_once_with("Test log message")


def test_create_logger_raises_error_with_invalid_config():
    log_config = {"invalid": "config"}

    with pytest.raises(Exception):
        create_logger(log_config)
