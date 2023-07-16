# flake8: noqa: S105
from http import HTTPStatus

import jwt
import pytest
from fastapi import HTTPException

from service.handlers.tokens import verify_token


def test_uuid_is_returned_when_jwt_is_valid() -> None:
    secret = "test_secret"
    algorithm = "HS256"
    uuid = "test_uuid"
    token = jwt.encode({"sub": uuid}, secret, algorithm=algorithm)

    result = verify_token(token, secret, algorithm)

    assert result == uuid


def test_unauthorized_error_is_raised_when_jwt_is_invalid() -> None:
    secret = "test_secret"
    algorithm = "HS256"
    invalid_token = "invalid_token"

    with pytest.raises(HTTPException) as e:
        verify_token(invalid_token, secret, algorithm)

    assert e.value.status_code == HTTPStatus.UNAUTHORIZED
    assert e.value.detail == "Invalid credentials"


def test_unauthorized_error_is_raised_when_jwt_is_not_signed_with_same_secret() -> None:
    secret = "test_secret"
    wrong_secret = "wrong_secret"
    algorithm = "HS256"
    uuid = "test_uuid"
    token = jwt.encode({"sub": uuid}, secret, algorithm=algorithm)

    with pytest.raises(HTTPException) as e:
        verify_token(token, wrong_secret, algorithm)

    assert e.value.status_code == HTTPStatus.UNAUTHORIZED
    assert e.value.detail == "Invalid credentials"
