import logging

from fastapi import Depends
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session

from service.api.exceptions import UserAlreadyExistsError
from service.database.exceptions import UserCreationError
from service.database.models import User
from service.database.session import create_database_session


class DataHandler:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user(self, username: str) -> User:
        logging.debug("Attempting to get user %s", username)
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, hashed_password: str) -> User:
        logging.info("Attempting to create user %s", username)
        if self.get_user(username):
            msg = "User %s already exists" % username
            logging.info(msg)
            raise UserAlreadyExistsError

        user = User(username=username, hashed_password=hashed_password)
        try:
            self.db.add(user)
            logging.info("User %s created", username)
        except IntegrityError as e:
            msg = "Error creating user %s" % username
            logging.exception(msg)
            raise UserCreationError(msg) from e
        return user


def get_data_handler(
    db_session: Session = Depends(create_database_session),
) -> DataHandler:
    return DataHandler(db_session)
