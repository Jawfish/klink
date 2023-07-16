from datetime import timedelta
from http import HTTPStatus

from common.api.schemas.user import InternalUserIdentity, UserTokenResponse
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from service.config import Config, get_config
from service.handlers.tokens import create_token, verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


@router.get("/user-identity", response_model=InternalUserIdentity)
def get_user_identity(
    token: str = Depends(oauth2_scheme),
    config: Config = Depends(get_config),
) -> InternalUserIdentity:
    """Expects a JWT token and responds with the user's UUID if it's valid."""
    uuid = verify_token(token, config.jwt_secret, config.jwt_algorithm)
    return InternalUserIdentity(uuid=uuid)


@router.post("login")
def login() -> None:
    """Expects a username and password responds with a JWT if they're valid."""


def logout() -> None:
    """Invalidates the user's JWT."""


@router.post("register", status_code=HTTPStatus.CREATED)
def register() -> None:
    """Expects a username and password, then creates a user, responding with a JWT."""


# This is not yet implemented in the serivce, so there's no route for it.
def refresh(
    refresh_token: str,
    config: Config = Depends(get_config),
) -> UserTokenResponse:
    """Expects a refresh JWT and responds with a new access JWT if it's valid."""
    user_uuid = verify_token(refresh_token, config.jwt_secret, config.jwt_algorithm)
    access_token = create_token(
        data={"sub": user_uuid},
        secret=config.jwt_secret,
        algorithm=config.jwt_algorithm,
        expires_delta=timedelta(minutes=15),
    )
    return UserTokenResponse(access_token=access_token)
