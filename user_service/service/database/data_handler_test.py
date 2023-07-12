import pytest
from service.api.schema import UserIn
from service.api.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserCreationError,
    UserDoesNotExistError,
)
from service.database.data_handler import DataHandler
from service.database.models import User
from argon2 import PasswordHasher, exceptions

ph = PasswordHasher()


def test_verify_user_verifies_valid_user_data(db, valid_user_in):
    data_handler = DataHandler(db)
    expected_user = User(
        username=valid_user_in.username,
        hashed_password=ph.hash(valid_user_in.unhashed_password),
    )
    db.add(expected_user)
    db.commit()

    user = data_handler.verify_user(valid_user_in)

    assert user.username == expected_user.username
    assert ph.verify(user.hashed_password, valid_user_in.unhashed_password)


def test_verify_user_raises_user_does_not_exist_error(db, valid_user_in):
    data_handler = DataHandler(db)

    with pytest.raises(UserDoesNotExistError):
        data_handler.verify_user(valid_user_in)


def test_verify_user_raises_authentication_error_with_mismatched_password(
    db, valid_user_in
):
    data_handler = DataHandler(db)
    existing_user = User(
        username=valid_user_in.username,
        hashed_password=ph.hash("wrong_password"),
    )
    db.add(existing_user)
    db.commit()

    with pytest.raises(AuthenticationError):
        data_handler.verify_user(valid_user_in)


def test_create_user_creates_user_with_valid_data(db, valid_user_in):
    pass


def test_create_user_raises_user_already_exists_error_with_existing_user(
    db, valid_user_in
):
    pass


def test_create_user_raises_user_already_exists_error_with_existing_user(
    db, valid_user_in
):
    pass


# def test_create_user(db, user_in):
#     data_handler = DataHandler(db)

#     # User doesn't exist yet, should be created successfully
#     user = data_handler.create_user(user_in)
#     assert user is not None
#     assert user.username == user_in.username

#     # Trying to create the same user again should raise UserAlreadyExistsError
#     with pytest.raises(UserAlreadyExistsError):
#         data_handler.create_user(user_in)

#     # Trying to create a user with invalid data should raise UserCreationError
#     # Assuming that invalid data for the User model is handled in the model itself
#     user_in.username = "invalid data"
#     with pytest.raises(UserCreationError):
#         data_handler.create_user(user_in)
