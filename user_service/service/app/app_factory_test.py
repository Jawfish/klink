from fastapi import FastAPI


def test_app_factory_provides_valid_app_instance(app: FastAPI) -> None:
    assert isinstance(app, FastAPI)
