import pytest
from service.api.schema import UserOut
from service.api.routes import create_user, verify_user
from service.database.data_handler import DataHandler
from service.api.exceptions import (
    UserAlreadyExistsError,
    UserDoesNotExistError,
)


import uuid


@pytest.fixture
def mock_data_handler(mocker):
    return mocker.Mock(spec=DataHandler)


class MockUserOut:
    def __init__(self, username, uuid):
        self.username = username
        self.uuid = uuid


class MockVerifyUserOut:
    def __init__(self, username, uuid):
        self.username = username
        self.uuid = uuid


def test_user_creation_succeeds_with_valid_data(mock_data_handler, valid_user_in):
    mock_user = MockUserOut(username="TestUser", uuid=uuid.uuid4())
    mock_data_handler.create_user.return_value = mock_user

    response = create_user(valid_user_in, mock_data_handler)

    mock_data_handler.create_user.assert_called_once()
    assert response == UserOut(username=mock_user.username, uuid=mock_user.uuid)


def test_existing_user_prevents_new_user_creation(mock_data_handler, valid_user_in):
    mock_data_handler.create_user.side_effect = UserAlreadyExistsError()

    with pytest.raises(UserAlreadyExistsError):
        create_user(valid_user_in, mock_data_handler)


def test_user_verification_succeeds_with_valid_data(mock_data_handler, valid_user_in):
    mock_verify_user = MockVerifyUserOut(username="TestUser", uuid=uuid.uuid4())
    mock_data_handler.verify_user.return_value = mock_verify_user

    response = verify_user(valid_user_in, mock_data_handler)

    mock_data_handler.verify_user.assert_called_once()

    assert response == UserOut(
        username=mock_verify_user.username, uuid=mock_verify_user.uuid
    )


def test_non_existent_user_cannot_be_verified(mock_data_handler, valid_user_in):
    mock_data_handler.verify_user.side_effect = UserDoesNotExistError()

    with pytest.raises(UserDoesNotExistError):
        verify_user(valid_user_in, mock_data_handler)
