from http import HTTPStatus

from common.api.schemas.user_schema import UserAuthData, UserContext
from fastapi import APIRouter, Depends

from service.database.user_handler import UserHandler, get_user_handler

router = APIRouter()


@router.post("/users", status_code=HTTPStatus.CREATED)
def create_user(
    user_in: UserAuthData,
    user_handler: UserHandler = Depends(get_user_handler),
) -> UserContext:
    user = user_handler.create_user(user_in)

    return user.to_user_out()


@router.post("/users/verify", status_code=HTTPStatus.OK)
def verify_user(
    user_in: UserAuthData,
    user_handler: UserHandler = Depends(get_user_handler),
) -> UserContext:
    user = user_handler.get_if_password_matches(user_in)

    return user.to_user_out()


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# @router.post("/token", status_code=HTTPStatus.OK)
# def login(
#     user_in: UserAuthData,
#     user_handler: UserHandler = Depends(get_user_handler),
#     jwt_secret_key: str = Depends(get_secret_key),
# ) -> dict:
#     user = user_handler.verify_user(user_in.username)
#     if not verify_password(user.password, user_in.hashed_password):
#         return {"message": msg.INVALID_CREDENTIALS_MSG}
#     return {"token": get_token(user_in, user_handler, jwt_secret_key)}
