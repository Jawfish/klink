import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from service.api.router import router
from service.handlers.credentials import ph


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
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
