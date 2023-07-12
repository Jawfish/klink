from fastapi import FastAPI


def test_create_app_returns_FastAPI_instance(app):
    assert isinstance(app, FastAPI)
