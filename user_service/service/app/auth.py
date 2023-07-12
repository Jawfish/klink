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
from service.database.data_handler import DataHandler
from service.database.models import User

ph = PasswordHasher()


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


def get_verified_user(user_in: UserIn, data_handler: DataHandler) -> User | None:
    username = user_in.username

    try:
        user = data_handler.verify_user(username)
    except UserDoesNotExistError:
        return None

    if not verify_password(user.password, user_in.unhashed_password):
        return None

    logging.debug("User %s verified", username)

    return user


def get_token(
    user_in: UserIn,
    data_handler: DataHandler,
    jwt_secret_key: str,
    jwt_algorithm: str = "HS256",
    expiry_minutes: int = 30,
) -> str:
    user = get_verified_user(user_in.username, user_in.unhashed_password, data_handler)

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
