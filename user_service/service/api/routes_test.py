import pytest
from service.api.schema import UserIn
from service.api.routes import create_user
from service.database.data_handler import DataHandler
from service.api.exceptions import (
    InvalidUsernameLengthError,
    ManagedException,
    UserAlreadyExistsError,
)
from fastapi.testclient import TestClient
from service.app_factory import create_app

from service.api import messages as msg
from service.exception_handlers import handle_managed_exception


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
    return UserIn(username="TestUser", password="TestPassword")


def test_create_user_success(mock_data_handler, user_in):
    mock_data_handler.create_user.return_value = None

    response = create_user(user_in, mock_data_handler)

    mock_data_handler.create_user.assert_called_once()
    assert response == {"message": msg.USER_CREATED_MSG}


def test_create_user_user_exists(mock_data_handler, user_in):
    mock_data_handler.create_user.side_effect = UserAlreadyExistsError()

    with pytest.raises(UserAlreadyExistsError):
        create_user(user_in, mock_data_handler)

    mock_data_handler.create_user.assert_called_once()


def test_create_user_empty_username(mock_data_handler, client):
    response = client.post("/user/", json={"username": "", "password": "TestPassword"})

    assert response.status_code == 400
    assert response.json() == {"detail": msg.INVALID_USERNAME_LENGTH_MSG}

    mock_data_handler.get_user.assert_not_called()
    mock_data_handler.create_user.assert_not_called()


def test_create_user_empty_password(mock_data_handler, client):
    response = client.post("/user/", json={"username": "TestUser", "password": ""})

    assert response.status_code == 400
    assert response.json() == {"detail": msg.INVALID_PASSWORD_LENGTH_MSG}
    mock_data_handler.get_user.assert_not_called()
    mock_data_handler.create_user.assert_not_called()
