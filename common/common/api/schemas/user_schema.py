import uuid

from pydantic import BaseModel, Field, field_validator

from common.api.exceptions.general_exceptions import EmptyFieldError


class UserAuthData(BaseModel):
    """This model is used to validate incoming user data."""
    username: str
    unhashed_password: str

    @field_validator("username")
    def validate_username(cls, username: str) -> str:  # noqa: N805
        if not username:
            raise EmptyFieldError
        return username

    @field_validator("unhashed_password")
    def validate_password(cls, password: str) -> str:  # noqa: N805
        """
        Validate that the password is not empty.

        Further validation, such as password strength, should be done in a higher-level
        service; it's not the responsibility of this service to validate an incoming
        password's strength, only to store the password securely. This guard is only to
        ensure that we don't try to store an empty password in the database.
        """
        if not password:
            raise EmptyFieldError
        return password


class UserContext(BaseModel):
    """
    This model is used to communicate the user context between services after the
    user has been authenticated.
    """
    uuid: uuid.UUID
    username: str = Field(..., min_length=1)
