from http import HTTPStatus

from common.api.exceptions import user_exceptions as ex
from common.api.schemas.user_schema import UserAuthData
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from service.database.user_handler import UserHandler


def test_user_creation_succeeds_with_valid_data(
    client: TestClient,
    valid_user_in: UserAuthData,
) -> None:
    response = client.post("/users", json=valid_user_in.model_dump())
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["username"] == valid_user_in.username
    assert "uuid" in data


def test_existing_user_prevents_new_user_creation(
    client: TestClient,
    valid_user_in: UserAuthData,
) -> None:
    client.post("/users", json=valid_user_in.model_dump())
    response = client.post("/users", json=valid_user_in.model_dump())
    assert response.status_code == ex.UserAlreadyExistsError.status_code


def test_user_verification_succeeds_with_valid_data(
    db: Session,
    client: TestClient,
    valid_user_in: UserAuthData,
) -> None:
    # create user directly in the database so we can verify it
    # use the user_handler to create the user instead of the route
    # to decouple this test from the user creation route test
    user_handler = UserHandler(db)
    user_handler.create_user(valid_user_in)

    response = client.post("/users/verify", json=valid_user_in.model_dump())
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["username"] == valid_user_in.username
    assert "uuid" in data


def test_non_existent_user_cannot_be_verified(client: TestClient) -> None:
    non_existent_user = UserAuthData(
        username="non_existent_user",
        unhashed_password="password",  # noqa: S106
    )
    response = client.post("/users/verify", json=non_existent_user.model_dump())
    assert response.status_code == ex.UserDoesNotExistError.status_code
