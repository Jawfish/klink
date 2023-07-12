import uuid

import pytest

from common.api.exceptions.general_exceptions import EmptyFieldError
from common.api.schemas.user_schema import UserAuthData, UserContext


@pytest.fixture
def valid_password() -> str:
    return "TestPassword"


@pytest.fixture
def valid_username() -> str:
    return "TestUser"


@pytest.fixture
def valid_uuid() -> uuid.UUID:
    return uuid.uuid4()


class TestIncomingUserSchema:
    def test_valid_input_passes_validation(
        self,
        valid_username: str,
        valid_password: str,
    ) -> None:
        user_in = UserAuthData(username=valid_username, unhashed_password=valid_password)

        assert user_in.username == "TestUser"
        assert user_in.unhashed_password == valid_password

    def test_empty_username_raises_exception(self, valid_password: str) -> None:
        with pytest.raises(EmptyFieldError):
            UserAuthData(username="", unhashed_password=valid_password)

    def test_empty_password_raises_exception(self, valid_username: str) -> None:
        with pytest.raises(EmptyFieldError):
            UserAuthData(username=valid_username, unhashed_password="")

    def test_empty_username_and_password_raises_exception(self) -> None:
        with pytest.raises(EmptyFieldError):
            UserAuthData(username="", unhashed_password="")


class TestOutgoingUserSchema:
    def test_valid_input_passes_validation(
        self,
        valid_uuid: uuid.UUID,
        valid_username: str,
    ) -> None:
        user_out = UserContext(uuid=valid_uuid, username=valid_username)

        assert user_out.username == "TestUser"
        assert user_out.uuid == valid_uuid

    def test_invalid_uuid_raises_validation_error(self, valid_username: str) -> None:
        with pytest.raises(ValueError):
            UserContext(uuid="invalid_uuid", username=valid_username)

    def test_empty_username_raises_validation_error(
        self,
        valid_uuid: uuid.UUID,
    ) -> None:
        with pytest.raises(ValueError):
            UserContext(uuid=valid_uuid, username="")
