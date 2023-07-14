from collections.abc import Generator
from typing import Any

import pytest
from common.api.exceptions.exception_handlers import handle_managed_exception
from common.api.exceptions.managed_exception import ManagedException
from common.api.schemas.user_schema import UserAuthData
from common.app.fastapi import FastAPIServer
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from service.api.routes import router
from service.database.session import Base
from service.database.user_handler import UserHandler, get_user_handler


@pytest.fixture
def valid_user_in() -> UserAuthData:
    return UserAuthData(
        username="TestUser",
        unhashed_password="password123",  # noqa: S106
    )


@pytest.fixture
def app(db: Session) -> FastAPI:
    server = FastAPIServer(
        router=router,
        host="127.0.0.1",
        port=8000,
    )
    app = server.app
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
