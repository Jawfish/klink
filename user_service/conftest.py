# flake8: noqa: ANN001

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from service.api.exception_handlers import handle_managed_exception
from service.api.exceptions import ManagedException
from service.api.schema import UserIn

from service.database.session import Base

import pytest
from service.app.app_factory import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def valid_user_in():
    return UserIn(username="TestUser", unhashed_password="password123")


@pytest.fixture
def app():
    app = create_app()
    app.add_exception_handler(ManagedException, handle_managed_exception)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def db(postgresql):
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
