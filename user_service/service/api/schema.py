import re

from pydantic import BaseModel, validator

from service.api.exceptions import (
    InvalidPasswordLengthError,
    InvalidUsernameCharsError,
    InvalidUsernameLengthError,
)
from service.api.schema_consts import (
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
)


class UserIn(BaseModel):
    username: str
    password: str

    @validator("username")
    def validate_username(cls, username: str) -> str:  # noqa: N805
        min_username_length = MIN_USERNAME_LENGTH
        max_username_length = MAX_USERNAME_LENGTH
        if not min_username_length <= len(username) <= max_username_length:
            raise InvalidUsernameLengthError
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise InvalidUsernameCharsError
        return username

    @validator("password")
    def validate_password(cls, password: str) -> str:  # noqa: N805
        min_password_length = MIN_PASSWORD_LENGTH
        max_password_length = MAX_PASSWORD_LENGTH
        if not min_password_length <= len(password) <= max_password_length:
            raise InvalidPasswordLengthError
        return password
