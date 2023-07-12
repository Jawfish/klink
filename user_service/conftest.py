# flake8: noqa: ANN001

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from service.api.schema import UserIn

from service.database.session import Base


@pytest.fixture
def valid_user_in():
    return UserIn(username="TestUser", unhashed_password="password123")


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
