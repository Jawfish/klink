import uuid

import pytest
from common.api.exceptions.handlers import handle_managed_exception
from common.api.exceptions.managed import ManagedException
from common.app.fastapi import FastAPIServer
from fastapi import FastAPI
from fastapi.testclient import TestClient

from service.api.router import router
from service.handlers.credentials import ph


@pytest.fixture
def app() -> FastAPI:
    server = FastAPIServer(
        router=router,
        host="127.0.0.1",
        port=8000,
    )
    app = server.app
    app.add_exception_handler(ManagedException, handle_managed_exception)
    return app


@pytest.fixture
def client(
    app: FastAPI,
) -> TestClient:
    return TestClient(app)


@pytest.fixture
def valid_uuid() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def valid_hashed_password() -> str:
    return ph.hash("valid_password")


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test_secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("USER_SERVICE_URL", "http://localhost:8001")
