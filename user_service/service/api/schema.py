import uuid

from pydantic import BaseModel, Field, validator

from service.api.exceptions import EmptyFieldError


class UserIn(BaseModel):
    username: str
    unhashed_password: str

    @validator("username")
    def validate_username(cls, username: str) -> str:  # noqa: N805
        if not username:
            raise EmptyFieldError
        return username

    @validator("unhashed_password")
    def validate_password(cls, password: str) -> str:  # noqa: N805
        if not password:
            raise EmptyFieldError
        return password


class UserOut(BaseModel):
    uuid: uuid.UUID
    username: str = Field(..., min_length=1)
