import json
import uuid
from http import HTTPStatus

import jwt
import pytest
import responses
from common.api.schemas.user import InternalUserIdentity, UserCredentials
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
        "/token",
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
        "/token",
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
        "/token",
        data={"username": "username_without_password"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@responses.activate
def test_successful_registration_with_valid_credentials(
    client: TestClient,
) -> None:
    user = UserCredentials(
        username="valid_username",
        unhashed_password="valid_password",  # noqa: S106
    )

    responses.add(
        responses.POST,
        "http://localhost:8001/users",
        status=HTTPStatus.CREATED,
        content_type="application/json",
    )

    response = client.post(
        "/register",
        content=user.model_dump_json(),
    )

    assert response.status_code == HTTPStatus.CREATED


@responses.activate
def test_registration_fails_when_user_already_exists(
    client: TestClient,
) -> None:
    user = UserCredentials(
        username="existing_username",
        unhashed_password="valid_password",  # noqa: S106
    )

    responses.add(
        responses.POST,
        "http://localhost:8001/users",
        status=HTTPStatus.CONFLICT,
        content_type="application/json",
    )

    response = client.post(
        "/register",
        content=user.model_dump_json(),
    )

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.parametrize(
    "username,password,expected_status",
    [
        ("valid_username", "", HTTPStatus.UNPROCESSABLE_ENTITY),
        ("", "valid_password", HTTPStatus.UNPROCESSABLE_ENTITY),
        ("", "", HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
@responses.activate
def test_registration_fails_for_invalid_inputs(
    client: TestClient,
    username: str,
    password: str,
    expected_status: HTTPStatus,
) -> None:
    responses.add(
        responses.POST,
        "http://localhost:8001/users",
        status=expected_status,
        content_type="application/json",
    )

    response = client.post(
        "/register",
        data={"username": username, "password": password},
    )

    assert response.status_code == expected_status
