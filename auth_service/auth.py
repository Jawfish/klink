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







####### a #######

import datetime
import logging
import os

import jwt
from argon2 import PasswordHasher, exceptions

from service.api.exceptions import (
    AuthenticationError,
    InternalError,
    UserDoesNotExistError,
)
from service.api.schema import UserIn
from service.database.models import User
from service.database.user_handler import UserHandler

ph = PasswordHasher()


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# @router.post("/token", status_code=HTTPStatus.OK)
# def login(
#     user_in: UserAuthData,
#     user_handler: UserHandler = Depends(get_user_handler),
#     jwt_secret_key: str = Depends(get_secret_key),
# ) -> dict:
#     user = user_handler.verify_user(user_in.username)
#     if not verify_password(user.password, user_in.hashed_password):
#         return {"message": msg.INVALID_CREDENTIALS_MSG}
#     return {"token": get_token(user_in, user_handler, jwt_secret_key)}



def get_secret_key() -> str:
    return os.getenv("JWT_SECRET_KEY")


def hash_password(password: str) -> str:
    try:
        hashed_password = ph.hash(password)
    except exceptions.HashingError:
        logging.exception("Failed to hash password")
        raise InternalError from None
    else:
        return hashed_password


def verify_password(hashed_password: str, password: str) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except exceptions.VerifyMismatchError:
        return False
    except Exception:
        logging.exception("Failed to verify password due to an unexpected error")
        raise InternalError from None


def get_verified_user(user_in: UserIn, user_handler: UserHandler) -> User | None:
    username = user_in.username

    try:
        user = user_handler.get_if_password_matches(username)
    except UserDoesNotExistError:
        return None

    if not verify_password(user.password, user_in.unhashed_password):
        return None

    logging.debug("User %s verified", username)

    return user


def get_token(
    user_in: UserIn,
    user_handler: UserHandler,
    jwt_secret_key: str,
    jwt_algorithm: str = "HS256",
    expiry_minutes: int = 30,
) -> str:
    user = get_verified_user(user_in.username, user_in.unhashed_password, user_handler)

    if not user:
        raise AuthenticationError(detail="Could not validate user to get token")

    token_data = {
        "sub": user.uuid,
        "exp": datetime.datetime.now(
            tz=datetime.timezone.utc,
        )
        + datetime.timedelta(minutes=expiry_minutes),
    }

    logging.debug("Token created for user %s", user_in.username)

    return jwt.encode(token_data, jwt_secret_key, algorithm=jwt_algorithm)


def validate_token(token: str, jwt_key: str, jwt_algorithm: str = "HS256") -> str:
    try:
        token_data = jwt.decode(token, jwt_key, algorithms=[jwt_algorithm])
    except jwt.exceptions.InvalidTokenError:
        raise AuthenticationError(detail="Invalid token") from None

    return token_data["sub"]
