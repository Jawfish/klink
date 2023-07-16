import pytest
from common.api.exceptions.user import (
    UserAlreadyExistsError,
)
from common.api.schemas.user import CreateUserRequest
from sqlalchemy.orm import Session

from service.database.user_handler import UserHandler


def test_user_creation_succeeds_with_valid_data(
    db: Session,
    create_user_payload: CreateUserRequest,
) -> None:
    user_handler = UserHandler(db)

    user = user_handler.create_user(create_user_payload)

    assert user is not None
    assert user.username == create_user_payload.username
    assert user.hashed_password == create_user_payload.hashed_password


def test_existing_user_prevents_new_user_creation(
    db: Session,
    create_user_payload: CreateUserRequest,
) -> None:
    user_handler = UserHandler(db)

    user = user_handler.create_user(create_user_payload)
    assert user is not None
    assert user.username == create_user_payload.username

    with pytest.raises(UserAlreadyExistsError):
        user_handler.create_user(create_user_payload)


def test_retrieval_of_user_by_username_succeeds(
    db: Session,
    create_user_payload: CreateUserRequest,
) -> None:
    user_handler = UserHandler(db)

    user = user_handler.create_user(create_user_payload)
    assert user is not None

    retrieved_user = user_handler.get_by_username(create_user_payload.username)
    assert retrieved_user is not None
    assert retrieved_user.username == create_user_payload.username


def test_retrieval_of_user_by_uuid_succeeds(
    db: Session,
    create_user_payload: CreateUserRequest,
) -> None:
    user_handler = UserHandler(db)

    user = user_handler.create_user(create_user_payload)
    assert user is not None

    retrieved_user = user_handler.get_by_uuid(user.uuid)
    assert retrieved_user is not None
    assert retrieved_user.uuid == user.uuid


def test_user_creation_fails_with_duplicate_username(
    db: Session,
    create_user_payload: CreateUserRequest,
) -> None:
    user_handler = UserHandler(db)

    user_handler.create_user(create_user_payload)

    with pytest.raises(UserAlreadyExistsError):
        user_handler.create_user(create_user_payload)
