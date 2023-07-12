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


def test_user_in_validation_succeeds_with_valid_input(valid_username, valid_password):
    user_in = UserIn(username=valid_username, unhashed_password=valid_password)

    assert user_in.username == "TestUser"
    assert user_in.unhashed_password == valid_password


def test_user_in_empty_username_raises_empty_field_exception(valid_password):
    with pytest.raises(EmptyFieldError):
        UserIn(username="", unhashed_password=valid_password)


def test_user_in_empty_password_raises_empty_field_exception(valid_username):
    with pytest.raises(EmptyFieldError):
        UserIn(username=valid_username, unhashed_password="")


def test_user_in_empty_username_and_password_raises_empty_field_exception():
    with pytest.raises(EmptyFieldError):
        UserIn(username="", unhashed_password="")


def test_user_out_validation_succeeds_with_valid_input(valid_uuid, valid_username):
    user_out = UserOut(uuid=valid_uuid, username=valid_username)

    assert user_out.username == "TestUser"
    assert user_out.uuid == valid_uuid


def test_user_out_model_raises_validation_error_with_invalid_uuid(valid_username):
    with pytest.raises(ValueError):
        UserOut(uuid="invalid_uuid", username=valid_username)


def test_user_out_model_raises_validation_error_with_empty_username(valid_uuid):
    with pytest.raises(ValueError):
        UserOut(uuid=valid_uuid, username="")
