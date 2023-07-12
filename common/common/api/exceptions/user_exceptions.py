"""User service exceptions."""

from http import HTTPStatus

from common.api.exceptions.managed_exception import ManagedException


class UserAlreadyExistsError(ManagedException):
    """Raised when the user already exists in the database"""

    status_code = HTTPStatus.CONFLICT
    detail = "User already exists"


class AuthenticationError(ManagedException):
    """Raised when the user cannot be authenticated"""

    status_code = HTTPStatus.UNAUTHORIZED
    detail = "User could not be authenticated"

class UserDoesNotExistError(ManagedException):
    """Raised when the user does not exist in the database"""

    status_code = HTTPStatus.NOT_FOUND
    detail = "User does not exist"


class UserCreationError(ManagedException):
    """Raised when the user could not be created in the database"""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    detail = "User could not be created"


class PasswordNotHashedError(ManagedException):
    """Raised when the provided password is not a valid argon2 hash"""

    status_code = HTTPStatus.BAD_REQUEST
    detail = "Password not hashed"
