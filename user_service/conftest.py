from collections.abc import Generator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from service.api.exception_handlers import handle_managed_exception
from service.api.exceptions import ManagedException
from service.api.schema import UserIn
from service.app.app_factory import create_app
from service.database.data_handler import DataHandler, get_data_handler
from service.database.session import Base


@pytest.fixture
def valid_user_in() -> UserIn:
    return UserIn(username="TestUser", unhashed_password="password123")  # noqa: S106


@pytest.fixture
def app(db: Session) -> FastAPI:
    app = create_app()
    app.add_exception_handler(ManagedException, handle_managed_exception)
    app.dependency_overrides[get_data_handler] = lambda: DataHandler(db)
    return app


@pytest.fixture
def client(
    app: FastAPI,
) -> TestClient:
    return TestClient(app)


@pytest.fixture
def db(postgresql: Any) -> Generator[Session, None, None]:  # noqa: ANN401
    session = sessionmaker(autocommit=False, autoflush=False)
    dsn = postgresql.info.dsn
    dsn_dict = dict(s.split("=") for s in dsn.split())
    sqlalchemy_dsn = f"postgresql://{dsn_dict['user']}@{dsn_dict['host']}:{dsn_dict['port']}/{dsn_dict['dbname']}"

    engine = create_engine(sqlalchemy_dsn)
    Base.metadata.create_all(bind=engine)
    session.configure(bind=engine)
    s = session()
    yield s
    s.close()
    Base.metadata.drop_all(bind=engine)
