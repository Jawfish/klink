# flake8: noqa: S105, S106

import uuid
from http import HTTPStatus

import pytest
import responses
from argon2.exceptions import VerifyMismatchError
from requests.exceptions import HTTPError

from service.handlers.credentials import (
    create_user,
    get_authenticated_uuid,
    ph,
    retrieve_hashed_password,
    verify_password,
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
        json_response = {"hashed_password": hashed_password, "uuid": str(uuid.uuid4())}
        status = HTTPStatus.OK

    responses.add(responses.GET, test_url, json=json_response, status=status)


def mock_user_creation_endpoint(
    _: str,
    __: str,
    conflict: bool = False,  # noqa: FBT001, FBT002
) -> None:
    test_url = "http://localhost:8001/users"
    if conflict:
        json_response = {"detail": "User already exists"}
        status = HTTPStatus.CONFLICT
    else:
        json_response = {"uuid": str(uuid.uuid4())}
        status = HTTPStatus.CREATED

    responses.add(responses.POST, test_url, json=json_response, status=status)


@responses.activate
def test_hashed_password_is_recieved_for_valid_user() -> None:
    mock_user_identity_endpoint("test_username", "hashed_password")

    service_url = "http://localhost:8001"

    data = retrieve_hashed_password("test_username", service_url)

    assert len(responses.calls) == 1
    assert data.hashed_password == "hashed_password"


@pytest.mark.parametrize(
    "username,expected_status",
    [
        ("wrong_username", HTTPStatus.UNAUTHORIZED),
        ("", HTTPStatus.BAD_REQUEST),
    ],
)
@responses.activate
def test_hashed_password_retrieval_fails_for_invalid_user(
    username: str,
    expected_status: HTTPStatus,
) -> None:
    mock_user_identity_endpoint(username)

    service_url: str = "http://localhost:8001"

    with pytest.raises(HTTPError) as excinfo:
        retrieve_hashed_password(username, service_url)
        assert excinfo.value.response.status_code == expected_status


def test_correct_password_verifies_successfully() -> None:
    hashed_password = ph.hash("test_password")
    verify_password("test_password", hashed_password)


def test_incorrect_password_fails_verification() -> None:
    hashed_password = ph.hash("test_password")
    with pytest.raises(VerifyMismatchError):
        verify_password("wrong_password", hashed_password)


@responses.activate
def test_valid_user_is_successfully_authenticated() -> None:
    hashed_password = ph.hash("test_password")
    mock_user_identity_endpoint("test_username", hashed_password)

    username = "test_username"
    unhashed_password = "test_password"
    service_url = "http://localhost:8001"

    uuid = get_authenticated_uuid(username, unhashed_password, service_url)

    assert uuid is not None


@responses.activate
def test_authentication_fails_for_invalid_user() -> None:
    hashed_password = ph.hash("test_password")
    mock_user_identity_endpoint("test_username", hashed_password)

    username = "test_username"
    wrong_unhashed_password = "wrong_password"
    service_url = "http://localhost:8001"

    with pytest.raises(VerifyMismatchError):
        get_authenticated_uuid(username, wrong_unhashed_password, service_url)


@responses.activate
def test_user_is_successfully_created() -> None:
    mock_user_creation_endpoint("test_username", ph.hash("test_password"))

    service_url = "http://localhost:8001"

    create_user("test_username", "test_password", service_url)

    assert len(responses.calls) == 1


@responses.activate
def test_user_creation_fails_when_user_already_exists() -> None:
    mock_user_creation_endpoint(
        "test_username",
        ph.hash("test_password"),
        conflict=True,
    )

    service_url = "http://localhost:8001"

    with pytest.raises(HTTPError) as excinfo:
        create_user("test_username", "test_password", service_url)

    assert excinfo.value.response.status_code == HTTPStatus.CONFLICT


@pytest.mark.parametrize(
    "username,password,expected_status",
    [
        ("test_username", "", HTTPStatus.BAD_REQUEST),
        ("", "test_password", HTTPStatus.BAD_REQUEST),
        ("", "", HTTPStatus.BAD_REQUEST),
    ],
)
@responses.activate
def test_user_creation_fails_for_invalid_inputs(
    username: str,
    password: str,
    expected_status: HTTPStatus,
) -> None:
    service_url: str = "http://localhost:8001"

    responses.add(
        responses.POST,
        f"{service_url}/users",
        status=expected_status,
    )

    with pytest.raises(HTTPError) as excinfo:
        create_user(username, password, service_url)

    assert excinfo.value.response.status_code == expected_status
