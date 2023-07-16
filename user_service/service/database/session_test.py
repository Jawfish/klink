from typing import Any
from unittest import mock
from unittest.mock import patch

import pytest
from common.api.exceptions.general import InternalError
from psycopg2 import OperationalError
from sqlalchemy import engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from service.database.session import SQLAlchemyConnector, create_database_session


@pytest.fixture
def db_connector() -> SQLAlchemyConnector:
    return SQLAlchemyConnector(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
    )


def test_database_connector_is_initialized_correctly(
    db_connector: SQLAlchemyConnector,
) -> None:
    assert db_connector is not None
    assert isinstance(db_connector.engine, engine.Engine)


def test_handling_of_operational_errors_by_database_connector(
    db_connector: SQLAlchemyConnector,
) -> None:
    mock_session = mock.create_autospec(Session, instance=True)
    mock_session.commit.side_effect = OperationalError
    db_connector.session_factory = mock.MagicMock(return_value=mock_session)

    with pytest.raises(OperationalError):
        session = next(db_connector.create_session())
        session.commit()  # this line will raise OperationalError


def test_handling_of_general_sqlalchemy_errors_by_database_connector(
    db_connector: SQLAlchemyConnector,
) -> None:
    mock_session = mock.create_autospec(Session, instance=True)
    mock_session.commit.side_effect = InternalError
    db_connector.session_factory = mock.MagicMock(return_value=mock_session)

    with pytest.raises(InternalError):
        session = next(db_connector.create_session())
        session.commit()


def test_database_session_creation_handles_sqlalchemy_errors() -> None:
    with patch(
        "service.database.session.SQLAlchemyConnector.__init__",
        side_effect=SQLAlchemyError,
    ), pytest.raises(SQLAlchemyError):
        next(create_database_session())


def test_database_session_creation_is_successful_when_no_errors_occurred(
    db_connector: SQLAlchemyConnector,
) -> None:
    session_generator = db_connector.create_session()
    session = next(session_generator, None)
    assert session is not None
    assert isinstance(session, Session)


def test_database_connector_establishes_a_database_connection_successfully(
    postgresql: Any,  # noqa: ANN401
) -> None:
    dsn = postgresql.info.dsn
    dsn_dict = dict(s.split("=") for s in dsn.split())
    sqlalchemy_dsn = f"postgresql://{dsn_dict['user']}@{dsn_dict['host']}:{dsn_dict['port']}/{dsn_dict['dbname']}"

    test_db_connector = SQLAlchemyConnector(sqlalchemy_dsn)

    assert test_db_connector is not None

    session_generator = test_db_connector.create_session()
    session = next(session_generator, None)
    assert session is not None
    assert isinstance(session, Session)
