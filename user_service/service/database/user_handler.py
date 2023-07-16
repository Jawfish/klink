import logging

from common.api.exceptions.user import (
    UserAlreadyExistsError,
)
from common.api.schemas.user import CreateUserRequest
from fastapi import Depends
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session

from service.database.models import User
from service.database.session import create_database_session


class UserHandler:
    """Handles database interactions involving the User model."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_uuid(self, uuid: str) -> User:
        return self.db.query(User).filter(User.uuid == uuid).first()

    def create_user(self, user_in: CreateUserRequest) -> User:
        if self.get_by_username(user_in.username) is not None:
            raise UserAlreadyExistsError

        user = User(
            username=user_in.username,
            hashed_password=user_in.hashed_password,
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


def get_user_handler(
    db_session: Session = Depends(create_database_session),
) -> UserHandler:
    return UserHandler(db_session)
