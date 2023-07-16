from common.api.schemas.user import (
    CreateUserRequest,
    InternalUserIdentity,
    UserAuthDataResponse,
)
from sqlalchemy.orm import Session

from service.database.user_handler import UserHandler


def test_user_identity_can_be_retrieved_from_user_model(
    db: Session,
    create_user_payload: CreateUserRequest,
) -> None:
    user_handler = UserHandler(db)
    user = user_handler.create_user(create_user_payload)

    user_identity = user.to_identity()
    assert isinstance(user_identity, InternalUserIdentity)


def test_auth_data_can_be_retrieved_from_user_model(
    db: Session,
    create_user_payload: CreateUserRequest,
) -> None:
    user_handler = UserHandler(db)
    user = user_handler.create_user(create_user_payload)

    user_auth_data = user.to_auth_data()
    assert isinstance(user_auth_data, UserAuthDataResponse)
    assert user_auth_data.uuid == user.uuid
    assert user_auth_data.hashed_password == user.hashed_password
