import uuid
from http import HTTPStatus

from common.api.exceptions import user as ex
from common.api.schemas.user import CreateUserRequest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from service.database.user_handler import UserHandler


def test_user_creation_succeeds_with_valid_data(
    client: TestClient,
    create_user_payload: CreateUserRequest,
) -> None:
    response = client.post("/users", json=create_user_payload.model_dump())
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert uuid.UUID(data["uuid"], version=4)


def test_existing_user_prevents_new_user_creation(
    client: TestClient,
    create_user_payload: CreateUserRequest,
) -> None:
    client.post("/users", json=create_user_payload.model_dump())
    response = client.post("/users", json=create_user_payload.model_dump())
    assert response.status_code == ex.UserAlreadyExistsError.status_code


def test_user_retrieval_by_uuid_returns_username(
    db: Session,
    client: TestClient,
    create_user_payload: CreateUserRequest,
) -> None:
    user_handler = UserHandler(db)
    user = user_handler.create_user(create_user_payload)
    user_uuid = str(user.uuid)

    response = client.get(
        f"/users/{user_uuid}/",
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data["username"] == create_user_payload.username


def test_user_retrieval_succeeds_if_user_exists(
    db: Session,
    client: TestClient,
    create_user_payload: CreateUserRequest,
) -> None:
    user_handler = UserHandler(db)
    user_handler.create_user(create_user_payload)

    response = client.get(
        f"/auth/{create_user_payload.username}/",
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert uuid.UUID(data["uuid"], version=4)
    assert data["hashed_password"] is not None


def test_user_retrieval_fails_if_user_does_not_exist(
    client: TestClient,
) -> None:
    response = client.get("/auth/nobody/")
    assert response.status_code == ex.UserDoesNotExistError.status_code
