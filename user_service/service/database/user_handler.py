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
        logging.info("Retrieving user %s", username)

        user = self.db.query(User).filter(User.username == username).first()

        if user is None:
            logging.info("User %s does not exist", username)
        else:
            logging.info("Retrieved user %s", username)

        return user

    def get_by_uuid(self, uuid: str) -> User:
        logging.info("Retrieving user by UUID: %s", uuid)

        user = self.db.query(User).filter(User.uuid == uuid).first()

        if user is None:
            logging.info("User with UUID %s does not exist", uuid)
        else:
            logging.info("Retrieved user with UUID %s", uuid)

        return user

    def create_user(self, user_in: CreateUserRequest) -> User:
        logging.info("Creating user %s", user_in.username)

        if self.get_by_username(user_in.username) is not None:
            logging.error("User %s already exists", user_in.username)
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
    logging.info("Creating user handler")
    return UserHandler(db_session)
