import uuid

import pytest
from fastapi import FastAPI


@pytest.fixture
def valid_password() -> str:
    return "TestPassword"


@pytest.fixture
def valid_username() -> str:
    return "TestUser"


@pytest.fixture
def valid_uuid() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def app() -> FastAPI:
    return FastAPI()
