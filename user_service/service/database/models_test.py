import pytest
from service.api.exceptions import PasswordNotHashedError
from service.database.models import User, ph


def test_saving_unhashed_password_raises_exception(db):
    non_hashed_password = "password123"
    user = User(username="TestUser", hashed_password=non_hashed_password)
    with pytest.raises(PasswordNotHashedError):
        db.add(user)
        db.commit()


def test_hashed_password_saves_successfully_in_database(db):
    hashed_password = ph.hash("password123")
    user = User(username="TestUser", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    user_from_db = db.query(User).filter_by(username="TestUser").first()
    assert user_from_db is not None
    assert ph.check_needs_rehash(user_from_db.hashed_password) is False
