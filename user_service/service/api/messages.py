# This file contains external-facing messages that are used in API responses.
# These messages are not intended to be used for logging or debugging purposes.

from service.api.schema_consts import (
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
)

INVALID_USERNAME_LENGTH_MSG = f"Username must be between {MIN_USERNAME_LENGTH} and {MAX_USERNAME_LENGTH} characters"  # noqa: E501
INVALID_PASSWORD_LENGTH_MSG = f"Password must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters"  # noqa: E501
USER_EXISTS_MSG = "User already exists"
USER_CREATED_MSG = "User created successfully"
GENERIC_INTERNAL_ERROR_MSG = "An internal error occurred while processing the request"
