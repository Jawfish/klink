from http import HTTPStatus
from service.api.schema import UserIn, UserOut
from service.api import exceptions as ex
from service.database.data_handler import DataHandler


def test_user_creation_succeeds_with_valid_data(client, valid_user_in: UserIn):
    response = client.post("/users", json=valid_user_in.dict())
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["username"] == valid_user_in.username
    assert "uuid" in data


def test_existing_user_prevents_new_user_creation(client, valid_user_in: UserIn):
    client.post("/users", json=valid_user_in.dict())
    response = client.post("/users", json=valid_user_in.dict())
    assert response.status_code == ex.UserAlreadyExistsError.status_code


def test_user_verification_succeeds_with_valid_data(db, client, valid_user_in: UserIn):
    # create user directly in the database so we can verify it
    # use the data_handler to create the user instead of the route
    # to decouple this test from the user creation route test
    data_handler = DataHandler(db)
    data_handler.create_user(valid_user_in)

    response = client.post("/users/verify", json=valid_user_in.dict())
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == valid_user_in.username
    assert "uuid" in data


def test_non_existent_user_cannot_be_verified(client):
    non_existent_user = UserIn(
        username="non_existent_user", unhashed_password="password"
    )
    response = client.post("/users/verify", json=non_existent_user.dict())
    assert response.status_code == ex.UserDoesNotExistError.status_code
