from http import HTTPStatus

import requests
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from common.api.schemas.user import UserAuthData
from fastapi import HTTPException

ph = PasswordHasher()


def retrieve_hashed_password(
    username: str,
    service_url: str,
) -> UserAuthData:
    response = None
    user_auth_data = None

    if not username:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Username is required",
        )

    try:
        response = requests.get(
            f"{service_url}/auth/{username}",
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        user_auth_data = UserAuthData(**data)

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


def verify_password(password: str, hashed_password: str) -> None:
    ph.verify(hashed_password, password)


def get_authenticated_uuid(
    username: str,
    unhashed_password: str,
    service_url: str,
) -> str:
    user = retrieve_hashed_password(
        username,
        service_url,
    )

    try:
        verify_password(unhashed_password, user.hashed_password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid credentials",
        ) from None
    else:
        return user.uuid
