import uuid

from pydantic import BaseModel, Field, field_validator


class UserAuthDataResponse(BaseModel):
    """
    Represents the data returned by the user service containing the information
    required for authentication purposes, such as when a user is logging in. The
    retrieving service can use this data to verify password hashes and create JWTs.

    Example flow:
    User Service > Auth Service
    """

    uuid: uuid.UUID
    hashed_password: str = Field(..., min_length=1)


class UserCredentials(BaseModel):
    """
    Represents incoming user credentials.

    It contains the username and unhashed password of the user so that the user can be
    authenticated by comparing the unhashed password against the hashed password that
    corresponds to the provided username.

    Example flow:
    Frontend > Gateway > Auth Service
    """

    username: str
    unhashed_password: str


class CreateUserRequest(BaseModel):
    """
    Represents user credentials required for registration purposes.

    It contains the username and hashed password of the user so that the user can be
    created in the database.

    Example flow:
    Auth Service > User Service
    """

    username: str
    hashed_password: str


class UserIdentityRequest(BaseModel):
    """
    Represents a request to retrieve user data from the user service.

    The user service matches the username in the request to the username in the
    database so that it can respond to the request with the appropriate user data.

    Example flow:
    Auth Service > User Service
    """

    username: str


class InternalUserIdentity(BaseModel):
    """Represents a user's identity for communication between services."""

    uuid: str

    @field_validator("uuid")
    def validate_uuid(cls, value: str) -> str:  # noqa: N805
        """Ensure that the UUID is a valid UUID."""

        if isinstance(value, uuid.UUID):
            return str(value)
        try:
            uuid.UUID(value)
        except ValueError as e:
            msg = "Invalid UUID: %s" % value
            raise ValueError(msg) from e
        return value


class UserTokenResponse(BaseModel):
    """
    Represents the response the client receives after the user has been authenticated.

    Example flow:
    Auth Service > Gateway > Frontend
    """

    token: str
