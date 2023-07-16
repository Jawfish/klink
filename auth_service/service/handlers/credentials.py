from http import HTTPStatus

import requests
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from common.api.schemas.user import UserAuthDataResponse, UserIdentityRequest
from fastapi import HTTPException

ph = PasswordHasher()


def retrieve_user_hashed_password(
    user_identity_request: UserIdentityRequest,
    service_url: str,
) -> UserAuthDataResponse:
    response = None
    user_auth_data = None

    if not user_identity_request.username:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
        )

    try:
        response = requests.get(
            f"{service_url}/auth/{user_identity_request.username}",
            timeout=5,
        )
        response.raise_for_status()
        user_auth_data: UserAuthDataResponse = response.json()

    except requests.exceptions.HTTPError:
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
            ) from None

        raise HTTPException(
            status_code=response.status_code,
        ) from None

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        ) from None

    return user_auth_data


def verify_user_password(password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, password)
    except VerifyMismatchError:
        return False
    return True
