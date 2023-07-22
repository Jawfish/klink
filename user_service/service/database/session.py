import logging
import os
from collections.abc import Generator

from common.api.exceptions.general import InternalError
from psycopg2 import OperationalError
from sqlalchemy import create_engine, engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()


class SQLAlchemyConnector:
    def __init__(self, url: str) -> None:
        logging.info("Establishing database connection")
        self.engine: engine.Engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        self.session_factory: sessionmaker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    def create_session(self) -> Generator[Session, None, None]:
        try:
            db_session: Session = self.session_factory()
            yield db_session
            db_session.commit()
        except OperationalError:
            logging.exception("Error establishing a database connection")
            raise
        except SQLAlchemyError:
            db_session.rollback()
            raise InternalError from None
        finally:
            db_session.close()


def create_database_session() -> Generator[Session, None, None]:
    logging.debug("Creating database session")
    # TODO: fail fast if database is not available (don't use a default value)
    db_connection = SQLAlchemyConnector(
        os.getenv(
            "SQLALCHEMY_DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
        ),
    )
    yield from db_connection.create_session()
