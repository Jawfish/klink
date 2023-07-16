from http import HTTPStatus

from common.api.exceptions.user import (
    UserDoesNotExistError,
)
from common.api.schemas.user import (
    CreateUserRequest,
    InternalUserIdentity,
    UserAuthDataResponse,
)
from fastapi import APIRouter, Depends

from service.database.user_handler import UserHandler, get_user_handler

router = APIRouter()


@router.post("/users", status_code=HTTPStatus.CREATED)
def create_user(
    payload: CreateUserRequest,
    user_handler: UserHandler = Depends(get_user_handler),
) -> InternalUserIdentity:
    """Create a new user in the database and return the created user's identity."""
    user = user_handler.create_user(payload)

    return user.to_identity()


@router.get("/auth/{username}/", status_code=HTTPStatus.OK)
def get_user_auth_data(
    username: str,
    user_handler: UserHandler = Depends(get_user_handler),
) -> UserAuthDataResponse:
    """Retrieve the data required to authenticate a user."""
    user = user_handler.get_by_username(username)

    if user is None:
        raise UserDoesNotExistError

    return user.to_auth_data()
