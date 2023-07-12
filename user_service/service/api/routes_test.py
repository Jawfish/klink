import pytest
from service.api.schema import UserIn, UserOut
from service.api.routes import create_user, verify_user
from service.database.data_handler import DataHandler
from service.api.exceptions import (
    EmptyFieldError,
    ManagedException,
    UserAlreadyExistsError,
    UserDoesNotExistError,
)

from fastapi.testclient import TestClient
from service.app.app_factory import create_app

from service.api.exception_handlers import handle_managed_exception
import uuid


class MockUserOut:
    def __init__(self, username, uuid):
        self.username = username
        self.uuid = uuid


class MockVerifyUserOut:
    def __init__(self, username, uuid):
        self.username = username
        self.uuid = uuid


@pytest.fixture
def app():
    app = create_app()
    app.add_exception_handler(ManagedException, handle_managed_exception)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_data_handler(mocker):
    return mocker.Mock(spec=DataHandler)


@pytest.fixture
def user_in():
    return UserIn(username="TestUser", unhashed_password="TestPassword")


def test_create_user_success(mock_data_handler, user_in):
    mock_user = MockUserOut(username="TestUser", uuid=uuid.uuid4())
    mock_data_handler.create_user.return_value = mock_user

    response = create_user(user_in, mock_data_handler)

    mock_data_handler.create_user.assert_called_once()
    assert response == UserOut(username=mock_user.username, uuid=mock_user.uuid)


def test_create_user_user_exists(mock_data_handler, user_in):
    mock_data_handler.create_user.side_effect = UserAlreadyExistsError()

    with pytest.raises(UserAlreadyExistsError):
        create_user(user_in, mock_data_handler)

    mock_data_handler.create_user.assert_called_once()


def test_verify_user_success(mock_data_handler, user_in):
    mock_verify_user = MockVerifyUserOut(username="TestUser", uuid=uuid.uuid4())
    mock_data_handler.verify_user.return_value = mock_verify_user

    response = verify_user(user_in, mock_data_handler)

    mock_data_handler.verify_user.assert_called_once()
    assert response == UserOut(
        username=mock_verify_user.username, uuid=mock_verify_user.uuid
    )


def test_verify_user_failure(mock_data_handler, user_in):
    mock_data_handler.verify_user.side_effect = UserDoesNotExistError()

    with pytest.raises(UserDoesNotExistError):
        verify_user(user_in, mock_data_handler)

    mock_data_handler.verify_user.assert_called_once()
