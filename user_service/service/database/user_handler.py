import logging

from argon2 import PasswordHasher, exceptions
from common.api.exceptions.user_exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserDoesNotExistError,
)
from common.api.schemas.user_schema import UserAuthData
from fastapi import Depends
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session

from service.database.models import User
from service.database.session import create_database_session

ph = PasswordHasher()


class UserHandler:
    """Handles database interactions involving the User model."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def get_if_password_matches(self, user_in: UserAuthData) -> User:
        """Retrieve a User object if the provided password passes hashing verification.

        The purpose of this method is to provide external services a way to verify
        a user's password without exposing password hashing implementaion details.
        Transmitting plaintext passwords over HTTPS between services is a conventional
        practice. By using this method, we keep the responsibility of password hashing
        in the user service's database layer.

        Raises:
            UserDoesNotExistError: Raised when the provided username does not exist in
            the database.
            AuthenticationError: Raised when the provided password does not match the
            stored hash, or if an unexpected error occurs during verification.

        Returns:
            User: The User object if password verification is successful.
        """
        user = self.get_by_username(user_in.username)
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

    def create_user(self, user_in: UserAuthData) -> User:
        if self.get_by_username(user_in.username) is not None:
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


def get_user_handler(
    db_session: Session = Depends(create_database_session),
) -> UserHandler:
    return UserHandler(db_session)
