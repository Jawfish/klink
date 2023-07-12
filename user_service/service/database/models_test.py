import pytest
from common.api.exceptions.user_exceptions import PasswordNotHashedError
from common.api.schemas.user_schema import UserAuthData
from sqlalchemy.orm import Session

from service.database.models import User, ph


def test_saving_unhashed_password_raises_exception(
    valid_user_in: UserAuthData,
    db: Session,
) -> None:
    user = User(
        username=valid_user_in.username,
        hashed_password=valid_user_in.unhashed_password,
    )
    with pytest.raises(PasswordNotHashedError):
        db.add(user)
        db.commit()


def test_hashed_password_saves_successfully_in_database(
    valid_user_in: UserAuthData,
    db: Session,
) -> None:
    hashed_password = ph.hash(valid_user_in.unhashed_password)
    user = User(username=valid_user_in.username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    user_from_db = db.query(User).filter_by(username="TestUser").first()
    assert user_from_db is not None
    assert ph.check_needs_rehash(user_from_db.hashed_password) is False
