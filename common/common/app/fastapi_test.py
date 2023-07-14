import pytest
from fastapi import FastAPI, APIRouter
from pytest_mock import MockerFixture

from common.app.fastapi import FastAPIServer, ServiceSetupError

TEST_IP_ADDRESS = "127.0.0.1"
TEST_PORT = 8000
TEST_LOG_CONFIG = {"version": 1}


@pytest.fixture
def api_router():
    return APIRouter()


@pytest.fixture
def fastapi_server(mocker: MockerFixture, app: FastAPI, api_router: APIRouter):
    mocker.patch("common.app.fastapi.load_config_file", return_value=TEST_LOG_CONFIG)
    mocker.patch("common.app.fastapi.configure_logging")
    return FastAPIServer(api_router, TEST_IP_ADDRESS, TEST_PORT)


def test_service_setup_completes_with_valid_configuration(
    fastapi_server: FastAPIServer,
    api_router: APIRouter,
) -> None:
    assert fastapi_server.router == api_router


def test_service_starts_successfully_with_valid_setup(
    mocker: MockerFixture,
    fastapi_server: FastAPIServer,
) -> None:
    mocker.patch("common.app.fastapi.Server")
    mocker.patch("common.app.fastapi.logging.info")

    fastapi_server.run()


@pytest.mark.parametrize(
    "host,port",
    [
        (None, TEST_PORT),
        (TEST_IP_ADDRESS, None),
    ],
)
def test_service_raises_exception_when_setup_is_incomplete(
    mocker: MockerFixture,
    api_router: APIRouter,
    host: str,
    port: int,
) -> None:
    mocker.patch("common.app.fastapi.logging.exception")
    with pytest.raises(ServiceSetupError):
        FastAPIServer(api_router, host, port)
