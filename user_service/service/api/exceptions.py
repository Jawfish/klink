from http import HTTPStatus


class ManagedException(Exception):  # noqa: N818
    """
    `ManagedException` is a base exception class for exceptions that are expected
    to occur within the application. These exceptions are associated with an HTTP
    status code and a detail message, which will be used in the error response.

    **Adding a custom exception:**
    ```python
    class UserAlreadyExistsError(ManagedException):
        status_code = 409
        detail = "User already exists"
    ```

    **Associating a handler with the exception:**

    1. Create a handler:
        ```python
        async def handle_managed_exception(exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
        ```
    2. Associate the handler with the exception:
        - Option 1 (using the `exception_handler` decorator):

        ```python
        @app.exception_handler(ManagedException)
        async def handle_managed_exception(request, exc):
            return exc.handler(request)
        ```
        - Option 2 (explicitly adding the handler to the app):

        ```python
        app = FastAPI()
        app.add_exception_handler(ManagedException, handle_managed_exception)
        ```
    """

    status_code: int = HTTPStatus.BAD_REQUEST
    detail: str = "An error occurred"

    def __init__(
        self,
        *,
        status_code: int | None = None,
        detail: str | None = None,
    ) -> None:
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail


class UserAlreadyExistsError(ManagedException):
    """Raised when the user already exists in the database"""

    status_code = HTTPStatus.CONFLICT
    detail = "User already exists"


class AuthenticationError(ManagedException):
    """Raised when the user cannot be authenticated"""

    status_code = HTTPStatus.UNAUTHORIZED
    detail = "User could not be authenticated"


class InternalError(ManagedException):
    """Raised when an internal error occurs, but we don't want to leak details"""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    detail = "Internal error"


class UserDoesNotExistError(ManagedException):
    """Raised when the user does not exist in the database"""

    status_code = HTTPStatus.NOT_FOUND
    detail = "User does not exist"


class EmptyFieldError(ManagedException):
    """Raised when a required field is empty"""

    status_code = HTTPStatus.BAD_REQUEST
    detail = "Required field is empty"


class UserCreationError(ManagedException):
    """Raised when the user could not be created in the database"""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    detail = "User could not be created"


class PasswordNotHashedError(ManagedException):
    """Raised when the provided password is not a valid argon2 hash"""

    status_code = HTTPStatus.BAD_REQUEST
    detail = "Password not hashed"
