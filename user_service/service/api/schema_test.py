import pytest
import uuid
from service.api.schema import UserIn, UserOut
from service.api.exceptions import EmptyFieldError


@pytest.fixture
def valid_password():
    return "TestPassword"


@pytest.fixture
def valid_username():
    return "TestUser"


@pytest.fixture
def valid_uuid():
    return uuid.uuid4()


class TestIncomingUserSchema:
    def test_valid_input_passes_validation(self, valid_username, valid_password):
        user_in = UserIn(username=valid_username, unhashed_password=valid_password)

        assert user_in.username == "TestUser"
        assert user_in.unhashed_password == valid_password

    def test_empty_username_raises_exception(self, valid_password):
        with pytest.raises(EmptyFieldError):
            UserIn(username="", unhashed_password=valid_password)

    def test_empty_password_raises_exception(self, valid_username):
        with pytest.raises(EmptyFieldError):
            UserIn(username=valid_username, unhashed_password="")

    def test_empty_username_and_password_raises_exception(self):
        with pytest.raises(EmptyFieldError):
            UserIn(username="", unhashed_password="")


class TestOutgoingUserSchema:
    def test_valid_input_passes_validation(self, valid_uuid, valid_username):
        user_out = UserOut(uuid=valid_uuid, username=valid_username)

        assert user_out.username == "TestUser"
        assert user_out.uuid == valid_uuid

    def test_invalid_uuid_raises_validation_error(self, valid_username):
        with pytest.raises(ValueError):
            UserOut(uuid="invalid_uuid", username=valid_username)

    def test_empty_username_raises_validation_error(self, valid_uuid):
        with pytest.raises(ValueError):
            UserOut(uuid=valid_uuid, username="")
