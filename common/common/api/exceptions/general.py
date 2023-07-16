"""Non-specific exceptions that can be raised by various services."""

from http import HTTPStatus

from common.api.exceptions.managed import ManagedException


class InternalError(ManagedException):
    """Raised when an internal error occurs, but we don't want to leak details"""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    detail = "Internal error"


class EmptyFieldError(ManagedException):
    """Raised when a required field is empty"""

    status_code = HTTPStatus.BAD_REQUEST
    detail = "Required field is empty"
