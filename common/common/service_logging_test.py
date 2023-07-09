import json
import logging
import logging.config
import pytest
from .service_logging import configure_logging, load_config_file
import os


def reset_logging():
    logging.getLogger().handlers = []
    logging.config.dictConfig({"version": 1})


@pytest.fixture(autouse=True)
def reset_logging_after_test():
    yield
    reset_logging()


def test_load_config_file(tmpdir):
    config_path = tmpdir.join("logging_config.json")
    config = {
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
    with open(config_path, "w") as f:
        json.dump(config, f)

    loaded_config = load_config_file(str(config_path))
    assert loaded_config == config


def test_load_config_file_raises_exceptions_for_invalid_files():
    with pytest.raises(FileNotFoundError):
        load_config_file("non_existent_file.json")

    with pytest.raises(json.JSONDecodeError):
        load_config_file(__file__)  # Try to load a Python file as JSON


def test_configure_logging(tmpdir):
    config = {
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": "DEBUG",
                "filename": str(tmpdir.join("test.log")),
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file"]},
    }

    configure_logging(config)

    logger = logging.getLogger()
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2

    file_handler = None
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
            file_handler = handler
            break

    assert file_handler is not None

    log_file_path = file_handler.baseFilename
    assert os.path.exists(log_file_path)


def test_configure_logging_raises_exception_for_invalid_config():
    invalid_config = {
        "version": 1,
        "handlers": {
            "console": {
                "class": "NonExistentHandler",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }

    with pytest.raises(ValueError):
        configure_logging(invalid_config)


def test_load_config_file_with_empty_file(tmpdir):
    config_path = tmpdir.join("empty_config.json")
    config_path.write("")
    with pytest.raises(json.JSONDecodeError):
        load_config_file(str(config_path))


def test_load_config_file_with_non_dict_json(tmpdir):
    config_path = tmpdir.join("invalid_config.json")
    config_path.write('["this is a list, not a dict"]')
    config = load_config_file(str(config_path))
    assert config == ["this is a list, not a dict"]


def test_configure_logging_with_no_handlers(caplog):
    config = {
        "version": 1,
        "root": {"level": "DEBUG", "handlers": []},
    }
    configure_logging(config)
    logger = logging.getLogger()
    assert logger.level == logging.DEBUG
    test_message = "Test message"
    logger.debug(test_message)
    assert test_message not in caplog.text


def test_configure_logging_with_invalid_handler_class():
    config = {
        "version": 1,
        "handlers": {
            "console": {
                "class": "InvalidHandlerClass",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
    with pytest.raises(ValueError):
        configure_logging(config)
