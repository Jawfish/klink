# flake8: noqa: S105
import uuid
from http import HTTPStatus

import jwt
import pytest
from fastapi import HTTPException

from service.handlers.tokens import get_identity


def test_valid_jwt_yields_correct_uuid() -> None:
    secret = "test_secret"
    algorithm = "HS256"
    test_uuid = str(uuid.uuid4())
    token = jwt.encode({"sub": test_uuid}, secret, algorithm=algorithm)

    result = get_identity(token, secret, algorithm)

    assert result.uuid == test_uuid


def test_missing_sub_claim_in_jwt_raises_error() -> None:
    secret = "test_secret"
    algorithm = "HS256"
    token_without_sub = jwt.encode({}, secret, algorithm=algorithm)

    with pytest.raises(HTTPException) as e:
        get_identity(token_without_sub, secret, algorithm)

    assert e.value.status_code == HTTPStatus.BAD_REQUEST


def test_invalid_jwt_raises_unauthorized_error() -> None:
    secret = "test_secret"
    algorithm = "HS256"
    invalid_token = "invalid_token"

    with pytest.raises(HTTPException) as e:
        get_identity(invalid_token, secret, algorithm)

    assert e.value.status_code == HTTPStatus.UNAUTHORIZED


def test_jwt_signed_with_different_secret_raises_unauthorized_error() -> None:
    secret = "test_secret"
    wrong_secret = "wrong_secret"
    algorithm = "HS256"
    test_uuid = str(uuid.uuid4())
    token = jwt.encode({"sub": test_uuid}, secret, algorithm=algorithm)

    with pytest.raises(HTTPException) as e:
        get_identity(token, wrong_secret, algorithm)

    assert e.value.status_code == HTTPStatus.UNAUTHORIZED
