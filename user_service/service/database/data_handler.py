import logging

from argon2 import PasswordHasher, exceptions
from fastapi import Depends
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session

from service.api.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserDoesNotExistError,
)
from service.api.schema import UserIn
from service.database.models import User
from service.database.session import create_database_session

ph = PasswordHasher()


class DataHandler:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def verify_user(self, user_in: UserIn) -> User:
        user = self.get_user_by_username(user_in.username)
        if user is None:
            logging.info("User %s does not exist", user_in.username)
            raise UserDoesNotExistError

        try:
            ph.verify(user.hashed_password, user_in.unhashed_password)
        except exceptions.VerifyMismatchError:
            raise AuthenticationError from None
        except Exception:
            logging.exception("Unexpected error verifying user %s", user_in.username)
            raise AuthenticationError from None
        else:
            return user

    def create_user(self, user_in: UserIn) -> User:
        if self.get_user_by_username(user_in.username) is not None:
            logging.info("User %s already exists", user_in.username)
            raise UserAlreadyExistsError

        user = User(
            username=user_in.username,
            hashed_password=ph.hash(user_in.unhashed_password),
        )

        self.db.add(user)
        try:
            self.db.commit()
            logging.info("User %s created", user_in.username)
        except IntegrityError:
            logging.exception("Error creating user %s", user_in.username)
            self.db.rollback()
            raise

        return user


def get_data_handler(
    db_session: Session = Depends(create_database_session),
) -> DataHandler:
    return DataHandler(db_session)
