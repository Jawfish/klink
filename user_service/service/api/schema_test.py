import pytest

from service.api.schema import UserIn
from service.api.exceptions import (
    InvalidPasswordLengthError,
    InvalidUsernameLengthError,
    InvalidUsernameCharsError,
)
from service.api.schema_consts import (
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
)


invalid_usernames = [
    ("", InvalidUsernameLengthError),
    ("   ", InvalidUsernameCharsError),
    ("a" * (MIN_USERNAME_LENGTH - 1), InvalidUsernameLengthError),
    ("a" * (MAX_USERNAME_LENGTH + 1), InvalidUsernameLengthError),
    (" valid_username ", InvalidUsernameCharsError),
    ("valid username", InvalidUsernameCharsError),
    ("valid_username$", InvalidUsernameCharsError),
    ("valid_username_ä", InvalidUsernameCharsError),
]

valid_usernames = [
    "a" * MIN_USERNAME_LENGTH,
    "a" * MAX_USERNAME_LENGTH,
    "valid_username",
    "valid_username_1",
    "valid_username_1_2_3",
    "1234567890",
]

invalid_passwords = [
    ("", InvalidPasswordLengthError),
    ("a" * (MIN_PASSWORD_LENGTH - 1), InvalidPasswordLengthError),
    ("a" * (MAX_PASSWORD_LENGTH + 1), InvalidPasswordLengthError),
]

valid_passwords = [
    "a" * MIN_PASSWORD_LENGTH,
    "a" * MAX_PASSWORD_LENGTH,
    "valid_password",
    "!@#$%^&*()_+~",
    "          ",
]


@pytest.mark.parametrize("username", valid_usernames)
@pytest.mark.parametrize("password", valid_passwords)
def test_user_in_schema_valid_input(username, password):
    user = UserIn(username=username, password=password)
    assert user.username == username
    assert user.password == password


@pytest.mark.parametrize("username,exception", invalid_usernames)
def test_user_in_schema_invalid_username(username, exception):
    with pytest.raises(exception):
        UserIn(username=username, password="valid_password")


@pytest.mark.parametrize("username", valid_usernames)
def test_user_in_schema_valid_username(username):
    user = UserIn(username=username, password="valid_password")
    assert user.username == username


@pytest.mark.parametrize("password,exception", invalid_passwords)
def test_user_in_schema_invalid_password(password, exception):
    with pytest.raises(exception):
        UserIn(username="valid_username", password=password)


@pytest.mark.parametrize("password", valid_passwords)
def test_user_in_schema_valid_password(password):
    user = UserIn(username="valid_username", password=password)
    assert user.password == password
