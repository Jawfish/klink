from collections.abc import Generator
from typing import Any

import pytest
from common.api.exceptions.handlers import handle_managed_exception
from common.api.exceptions.managed import ManagedException
from common.api.schemas.user import CreateUserRequest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from service.api.router import router
from service.database.session import Base
from service.database.user_handler import UserHandler, get_user_handler


@pytest.fixture
def create_user_payload() -> CreateUserRequest:
    return CreateUserRequest(
        username="TestUser",
        hashed_password="password123",  # noqa: S106
    )


@pytest.fixture
def app(db: Session) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(ManagedException, handle_managed_exception)
    app.dependency_overrides[get_user_handler] = lambda: UserHandler(db)
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
