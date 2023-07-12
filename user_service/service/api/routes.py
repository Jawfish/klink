from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from service.api.schema import UserIn, UserOut
from service.database.data_handler import DataHandler, get_data_handler

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@router.post("/users", status_code=HTTPStatus.CREATED)
def create_user(
    user_in: UserIn,
    data_handler: DataHandler = Depends(get_data_handler),
) -> UserOut:
    user = data_handler.create_user(user_in)

    return UserOut(username=user.username, uuid=user.uuid)


@router.post("/users/verify", status_code=HTTPStatus.OK)
def verify_user(
    user_in: UserIn,
    data_handler: DataHandler = Depends(get_data_handler),
) -> dict:
    user = data_handler.verify_user(user_in)

    return UserOut(username=user.username, uuid=user.uuid)


# @router.post("/token", status_code=HTTPStatus.OK)
# def login(
#     user_in: UserIn,
#     data_handler: DataHandler = Depends(get_data_handler),
#     jwt_secret_key: str = Depends(get_secret_key),
# ) -> dict:
#     user = data_handler.verify_user(user_in.username)
#     if not verify_password(user.password, user_in.hashed_password):
#         return {"message": msg.INVALID_CREDENTIALS_MSG}
#     return {"token": get_token(user_in, data_handler, jwt_secret_key)}
