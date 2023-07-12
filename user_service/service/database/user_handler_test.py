import pytest
from argon2 import PasswordHasher
from common.api.exceptions.user_exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserDoesNotExistError,
)
from common.api.schemas.user_schema import UserAuthData
from sqlalchemy.orm import Session

from service.database.models import User
from service.database.user_handler import UserHandler

ph = PasswordHasher()


def test_verification_succeeds_with_valid_user_data(
    db: Session,
    valid_user_in: UserAuthData,
) -> None:
    user_handler = UserHandler(db)
    expected_user = User(
        username=valid_user_in.username,
        hashed_password=ph.hash(valid_user_in.unhashed_password),
    )
    db.add(expected_user)
    db.commit()

    user = user_handler.get_if_password_matches(valid_user_in)

    assert user.username == expected_user.username
    assert ph.verify(user.hashed_password, valid_user_in.unhashed_password)


def test_verification_fails_for_non_existent_user(
    db: Session,
    valid_user_in: UserAuthData,
) -> None:
    user_handler = UserHandler(db)

    with pytest.raises(UserDoesNotExistError):
        user_handler.get_if_password_matches(valid_user_in)


def test_mismatched_password_raises_exception(
    db: Session,
    valid_user_in: UserAuthData,
) -> None:
    user_handler = UserHandler(db)
    existing_user = User(
        username=valid_user_in.username,
        hashed_password=ph.hash("wrong_password"),
    )
    db.add(existing_user)
    db.commit()

    with pytest.raises(AuthenticationError):
        user_handler.get_if_password_matches(valid_user_in)


def test_user_creation_succeeds_with_valid_data(
    db: Session,
    valid_user_in: UserAuthData,
) -> None:
    user_handler = UserHandler(db)

    user = user_handler.create_user(valid_user_in)

    assert user is not None
    assert user.username == valid_user_in.username
    assert ph.verify(user.hashed_password, valid_user_in.unhashed_password)


def test_existing_user_prevents_new_user_creation(
    db: Session,
    valid_user_in: UserAuthData,
) -> None:
    user_handler = UserHandler(db)

    user = user_handler.create_user(valid_user_in)
    assert user is not None
    assert user.username == valid_user_in.username

    with pytest.raises(UserAlreadyExistsError):
        user_handler.create_user(valid_user_in)


# def test_create_user(db, user_in):
#     user_handler = UserHandler(db)

#     # User doesn't exist yet, should be created successfully
#     user = user_handler.create_user(user_in)
#     assert user is not None
#     assert user.username == user_in.username

#     # Trying to create the same user again should raise UserAlreadyExistsError
#     with pytest.raises(UserAlreadyExistsError):
#         user_handler.create_user(user_in)

#     # Trying to create a user with invalid data should raise UserCreationError
#     # Assuming that invalid data for the User model is handled in the model itself
#     user_in.username = "invalid data"
#     with pytest.raises(UserCreationError):
#         user_handler.create_user(user_in)
