import json
import uuid
from http import HTTPStatus

import jwt
import responses
from common.api.schemas.user import InternalUserIdentity
from fastapi.testclient import TestClient


def test_valid_token_provides_user_identity(
    client: TestClient,
) -> None:
    test_secret = "test_secret"  # noqa: S105
    test_algorithm = "HS256"
    test_uuid = str(uuid.uuid4())
    test_token = jwt.encode({"sub": test_uuid}, test_secret, algorithm=test_algorithm)

    response = client.get(
        "/user-identity",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    identity = InternalUserIdentity(**response.json())

    assert response.status_code == HTTPStatus.OK
    assert identity.uuid == test_uuid


def test_invalid_token_results_in_unauthorized_status(client: TestClient) -> None:
    response = client.get(
        "/user-identity",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@responses.activate
def test_successful_login_with_correct_credentials(
    client: TestClient,
    valid_uuid: str,
    valid_hashed_password: str,
) -> None:
    user_auth_data = {
        "hashed_password": valid_hashed_password,
        "uuid": valid_uuid,
    }

    responses.add(
        responses.GET,
        "http://localhost:8001/auth/valid_username",
        body=json.dumps(user_auth_data),
        status=HTTPStatus.OK,
        content_type="application/json",
    )

    response = client.post(
        "/login",
        data={"username": "valid_username", "password": "valid_password"},
    )

    assert response.status_code == HTTPStatus.OK


@responses.activate
def test_invalid_credentials_result_in_unauthorized_status(
    client: TestClient,
    valid_hashed_password: str,
) -> None:
    user_auth_data = {
        "hashed_password": valid_hashed_password,
        "uuid": "valid_uuid",
    }

    responses.add(
        responses.GET,
        "http://localhost:8001/auth/invalid_username",
        body=json.dumps(user_auth_data),
        status=HTTPStatus.NOT_FOUND,
        content_type="application/json",
    )

    response = client.post(
        "/login",
        data={"username": "invalid_username", "password": "invalid_password"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@responses.activate
def test_missing_credentials_result_in_unprocessable_status(
    client: TestClient,
    valid_hashed_password: str,
) -> None:
    user_auth_data = {
        "hashed_password": valid_hashed_password,
        "uuid": "valid_uuid",
    }

    responses.add(
        responses.GET,
        "http://localhost:8001/auth/username_without_password",
        body=json.dumps(user_auth_data),
        status=HTTPStatus.UNPROCESSABLE_ENTITY,
        content_type="application/json",
    )

    response = client.post(
        "/login",
        data={"username": "username_without_password"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
