import pytest
from common.api.exceptions.handlers import handle_managed_exception
from common.api.exceptions.managed import ManagedException
from common.app.fastapi import FastAPIServer
from fastapi import FastAPI
from fastapi.testclient import TestClient

from service.api.router import router
from service.config import Config, get_config


def get_test_config() -> Config:
    return Config("test_secret", "HS256")


@pytest.fixture
def app() -> FastAPI:
    server = FastAPIServer(
        router=router,
        host="127.0.0.1",
        port=8000,
    )
    app = server.app
    app.add_exception_handler(ManagedException, handle_managed_exception)
    app.dependency_overrides[get_config] = get_test_config
    return app


@pytest.fixture
def client(
    app: FastAPI,
) -> TestClient:
    return TestClient(app)
