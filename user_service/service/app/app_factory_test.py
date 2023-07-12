from fastapi import FastAPI
import pytest
from service.app.app_factory import create_app


@pytest.fixture(scope="module")
def app():
    return create_app()


def test_create_app_returns_FastAPI_instance(app):
    assert isinstance(app, FastAPI)
