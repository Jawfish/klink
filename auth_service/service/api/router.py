from datetime import timedelta
from http import HTTPStatus

from common.api.schemas.user import AuthToken, InternalUserIdentity
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from service.config import JWTConfig, ServiceConfig, get_jwt_config, get_service_config
from service.handlers.credentials import get_authenticated_uuid
from service.handlers.tokens import create_token, get_identity

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


@router.get("/user-identity", response_model=InternalUserIdentity)
def get_user_identity(
    token: str = Depends(oauth2_scheme),
    jwt_config: JWTConfig = Depends(get_jwt_config),
) -> InternalUserIdentity:
    """Expects a JWT and responds with the user's UUID if it's valid."""
    return get_identity(token, jwt_config.jwt_secret, jwt_config.jwt_algorithm)


@router.post("/login", response_model=AuthToken)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    jwt_config: JWTConfig = Depends(get_jwt_config),
    service_config: ServiceConfig = Depends(get_service_config),
) -> AuthToken:
    """Expects a username and password responds with a JWT if they're valid."""
    uuid = get_authenticated_uuid(
        username=form_data.username,
        unhashed_password=form_data.password,
        service_url=service_config.user_service_url,
    )
    return create_token(data={"sub": uuid}, config=jwt_config)


def logout() -> None:
    """Invalidates the user's JWT."""


@router.post("register", status_code=HTTPStatus.CREATED)
def register() -> None:
    """Expects a username and password, then creates a user, responding with a JWT."""


# This is not yet implemented in the serivce, so there's no route for it.
def refresh(
    refresh_token: str,
    config: JWTConfig = Depends(get_jwt_config),
) -> AuthToken:
    """Expects a refresh JWT and responds with a new access JWT if it's valid."""
    user_uuid = get_identity(
        refresh_token,
        config.jwt_secret,
        config.jwt_algorithm,
    )
    access_token = create_token(
        data={"sub": user_uuid},
        config=config,
        expires_delta=timedelta(minutes=15),
    )
    return AuthToken(token=access_token)
