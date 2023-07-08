import logging
import os
from fluent.handler import FluentHandler
from .service_logging import LoggingConfig, configure_logging


def test_configure_logging_with_valid_config(tmpdir):
    configure_logging(
        config=LoggingConfig(
            service_name="test",
            logger_host="localhost",
            logger_port=24224,
            logging_level=logging.DEBUG,
            local_log_dir=str(tmpdir.join("test_logs")),
        )
    )

    logger = logging.getLogger()
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 3

    assert any(isinstance(handler, FluentHandler) for handler in logger.handlers)


def test_configure_logging_logs_to_file(tmpdir):
    configure_logging(
        config=LoggingConfig(
            service_name="test",
            logger_host="localhost",
            logger_port=24224,
            logging_level=logging.DEBUG,
            local_log_dir=str(tmpdir.join("test_logs")),
        )
    )

    logger = logging.getLogger()

    file_handler = None
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
            file_handler = handler
            break

    assert file_handler is not None

    log_dir = os.path.dirname(file_handler.baseFilename)
    expected_log_dir = "test_logs"
    assert log_dir.endswith(expected_log_dir)

    log_file_path = file_handler.baseFilename
    assert os.path.exists(log_file_path)

    expected_log_message = "This is a test log message"
    logger.info(expected_log_message)

    with open(log_file_path, "r") as log_file:
        log_contents = log_file.read()

    assert expected_log_message in log_contents
