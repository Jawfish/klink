# flake8: noqa: S105, S106

from http import HTTPStatus

import pytest
import responses
from common.api.schemas.user import UserIdentityRequest
from fastapi import HTTPException

from service.handlers.credentials import (
    ph,
    retrieve_user_hashed_password,
    verify_user_password,
)


def mock_user_identity_endpoint(
    username: str,
    hashed_password: str | None = None,
) -> None:
    test_url = f"http://localhost:8001/auth/{username}"
    if hashed_password is None:
        json_response = {"detail": "Not Found"}
        status = HTTPStatus.NOT_FOUND
    else:
        json_response = {"hashed_password": hashed_password}
        status = HTTPStatus.OK

    responses.add(responses.GET, test_url, json=json_response, status=status)


@responses.activate
def test_successful_retrieval_of_hashed_password_for_valid_user() -> None:
    mock_user_identity_endpoint("test_username", "hashed_password")

    user_identity_request = UserIdentityRequest(
        username="test_username",
        password="test_password",
    )
    service_url = "http://localhost:8001"

    response = retrieve_user_hashed_password(user_identity_request, service_url)

    assert len(responses.calls) == 1
    assert "hashed_password" in response
    assert response["hashed_password"] == "hashed_password"


@pytest.mark.parametrize(
    "username,expected_status",
    [
        ("wrong_username", HTTPStatus.UNAUTHORIZED),
        ("", HTTPStatus.BAD_REQUEST),
    ],
)
@responses.activate
def test_failed_retrieval_of_hashed_password_for_invalid_user(
    username: str,
    expected_status: HTTPStatus,
) -> None:
    mock_user_identity_endpoint(username)

    user_identity_request = UserIdentityRequest(
        username=username,
    )
    service_url: str = "http://localhost:8001"

    with pytest.raises(HTTPException) as excinfo:
        retrieve_user_hashed_password(user_identity_request, service_url)
        assert excinfo.value.status_code == expected_status


def test_password_verification_successful_for_correct_password() -> None:
    assert verify_user_password("test_password", ph.hash("test_password")) is True


def test_password_verification_fails_for_incorrect_password() -> None:
    assert verify_user_password("wrong_password", ph.hash("test_password")) is False
