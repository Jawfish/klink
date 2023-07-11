import pytest

from service.api.schema import UserIn
from service.api.exceptions import (
    InvalidPasswordLengthError,
    InvalidUsernameLengthError,
)
from service.api.schema_consts import (
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
)


def test_user_in_schema_valid_input():
    valid_username = "a" * MIN_USERNAME_LENGTH
    valid_password = "a" * MIN_PASSWORD_LENGTH
    user = UserIn(username=valid_username, password=valid_password)
    assert user.username == valid_username
    assert user.password == valid_password


def test_user_in_schema_username_too_short():
    invalid_username = "a" * (MIN_USERNAME_LENGTH - 1)
    with pytest.raises(InvalidUsernameLengthError):
        UserIn(username=invalid_username, password="valid_password")


def test_user_in_schema_username_too_long():
    invalid_username = "a" * (MAX_USERNAME_LENGTH + 1)
    with pytest.raises(InvalidUsernameLengthError):
        UserIn(username=invalid_username, password="valid_password")


def test_user_in_schema_password_too_short():
    invalid_password = "a" * (MIN_PASSWORD_LENGTH - 1)
    with pytest.raises(InvalidPasswordLengthError):
        UserIn(username="valid_username", password=invalid_password)


def test_user_in_schema_password_too_long():
    invalid_password = "a" * (MAX_PASSWORD_LENGTH + 1)
    with pytest.raises(InvalidPasswordLengthError):
        UserIn(username="valid_username", password=invalid_password)
