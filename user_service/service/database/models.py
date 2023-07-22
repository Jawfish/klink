import uuid

from common.api.schemas.user import InternalUserIdentity, UserAuthData
from sqlalchemy import UUID, Column, String
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from service.database.session import Base


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

    def to_identity(self) -> InternalUserIdentity:
        return InternalUserIdentity(uuid=str(self.uuid))

    def to_auth_data(self) -> UserAuthData:
        return UserAuthData(
            uuid=str(self.uuid),
            hashed_password=self.hashed_password,
        )
