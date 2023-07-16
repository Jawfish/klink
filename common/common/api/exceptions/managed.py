from http import HTTPStatus


class ManagedException(Exception):  # noqa: N818
    """Manage exceptions that are expected to occur within the application.

    These exceptions are associated with an HTTP
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
