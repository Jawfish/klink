import uuid
from http import HTTPStatus

import jwt
from common.api.schemas.user import InternalUserIdentity
from fastapi.testclient import TestClient


def test_user_identity_route_returns_correct_value_with_valid_token(
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


def test_user_identity_route_returns_401_with_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/user-identity",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "detail" in response.json()
    assert response.json()["detail"] == "Invalid credentials"
