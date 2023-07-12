import pytest
from fastapi import FastAPI
from pytest_mock import MockerFixture

from service.app.server import ServiceRunError, ServiceSetupError, run, setup

TEST_IP_ADDRESS = "127.0.0.1"
TEST_PORT = 8000
TEST_LOG_CONFIG = {"version": 1}


def test_service_setup_completes_with_valid_configuration(
    mocker: MockerFixture,
    app: FastAPI,
) -> None:
    mocker.patch("service.app.server.load_config_file", return_value=TEST_LOG_CONFIG)
    mocker.patch("os.getenv", side_effect=[TEST_IP_ADDRESS, str(TEST_PORT)])
    mocker.patch("service.app.server.configure_logging")
    mocker.patch("service.app.server.create_app", return_value=app)

    result = setup()

    assert result == (app, TEST_IP_ADDRESS, TEST_PORT, TEST_LOG_CONFIG)


def test_service_starts_successfully_with_valid_setup(
    mocker: MockerFixture,
    app: FastAPI,
) -> None:
    mocker.patch("service.app.server.Server")
    mocker.patch("service.app.server.logging.info")

    run(app, TEST_IP_ADDRESS, TEST_PORT, TEST_LOG_CONFIG)


@pytest.mark.parametrize(
    "app,host,port,log_config",
    [
        (None, None, TEST_PORT, TEST_LOG_CONFIG),
        (None, TEST_IP_ADDRESS, None, TEST_LOG_CONFIG),
        (None, TEST_IP_ADDRESS, TEST_PORT, None),
    ],
)
def test_service_raises_exception_when_setup_is_incomplete(
    mocker: MockerFixture,
    app: FastAPI,
    host: str,
    port: int,
    log_config: dict,
) -> None:
    mocker.patch("service.app.server.logging.exception")

    with pytest.raises(ServiceSetupError):
        run(app, host, port, log_config)


def test_service_raises_exception_when_an_unexpected_issue_occurs(
    mocker: MockerFixture,
    app: FastAPI,
) -> None:
    mocker.patch("service.app.server.Server.run", side_effect=Exception)
    mocker.patch("service.app.server.logging.exception")

    with pytest.raises(ServiceRunError):
        run(app, TEST_IP_ADDRESS, TEST_PORT, TEST_LOG_CONFIG)
