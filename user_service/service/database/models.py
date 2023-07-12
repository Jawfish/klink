import uuid

from argon2 import PasswordHasher, exceptions
from sqlalchemy import UUID, Column, String, event
from sqlalchemy.orm import Mapper
from sqlalchemy.orm.session import Connection
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from service.api.exceptions import PasswordNotHashedError
from service.database.session import Base

ph = PasswordHasher()


class User(Base):
    __tablename__ = "users"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        nullable=False,
        default=uuid.uuid4,
    )
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )


def ensure_password_is_hashed(
    _: Mapper,
    __: Connection,
    target: User,
) -> None:
    try:
        ph.check_needs_rehash(target.hashed_password)
    except exceptions.InvalidHash:
        raise PasswordNotHashedError from None


event.listen(User, "before_insert", ensure_password_is_hashed)
event.listen(User, "before_update", ensure_password_is_hashed)
