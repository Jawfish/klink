import requests
from argon2 import PasswordHasher
from common.api.schemas.user import CreateUserRequest, UserAuthData

ph = PasswordHasher()


def retrieve_hashed_password(
    username: str,
    service_url: str,
) -> UserAuthData:
    response = None

    response = requests.get(
        f"{service_url}/auth/{username}",
        timeout=5,
    )
    response.raise_for_status()
    data = response.json()
    return UserAuthData(**data)


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
    verify_password(unhashed_password, user.hashed_password)
    return user.uuid


def create_user(
    username: str,
    unhashed_password: str,
    service_url: str,
) -> None:
    hashed_password = ph.hash(unhashed_password)

    request = CreateUserRequest(username=username, hashed_password=hashed_password)
    response = requests.post(
        f"{service_url}/users",
        json=request.model_dump(),
        timeout=5,
    )
    response.raise_for_status()
