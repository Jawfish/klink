import sys
import traceback
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request
from fastapi import Response as FastAPIResponse
from flask import Flask, request
from flask import Response as FlaskResponse
from fluent import event, sender
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class FluentEventError(Exception):
    """Exception raised for errors in the Fluent event logging.

    Attributes:
        tag -- tag of the event that caused the error
        data -- data of the event that caused the error
        message -- explanation of the error
    """

    def __init__(self, tag: str, data: dict[str, Any], message: str) -> None:
        self.tag = tag
        self.data = data
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.tag} -> {self.data} : {self.message}"


class BaseLogger:
    def __init__(self, tag: str, fluentd_host: str, fluentd_port: int) -> None:
        self.fluentd_host = fluentd_host
        self.fluentd_port = fluentd_port
        sender.setup(tag, host=self.fluentd_host, port=self.fluentd_port)

    def log_event(self, tag: str, data: dict[str, Any]) -> None:
        """Log a custom event to Fluentd."""
        try:
            event.Event(tag, data)
        except FluentEventError as e:
            print(  # noqa: T201
                f"The logger middleware failed to send event to FluentD: {e}",
                file=sys.stderr,
            )
        except Exception as e:  # noqa: BLE001
            print(  # noqa: T201
                f"The logger middleware experienced an unexpected error: {e}",
                file=sys.stderr,
            )


class FluentLoggerFastAPIMiddleware(BaseLogger):
    """
    Middleware to log FastAPI requests to Fluentd.

    Args:
        app (FastAPI): FastAPI app
        fluentd_host (str): Fluentd host
        fluentd_port (int): Fluentd port

    Returns:
        None

    Usage:
        # Logging FastAPI requests
        app = FastAPI()
        app.add_middleware(
            FluentLoggerFastAPIMiddleware,
            tag="test",
            fluentd_host="localhost",
            fluentd_port=24224
        )

        # Logging application events
        logger = FluentLoggerFastAPIMiddleware("test", app, "localhost", 24224)
        logger.log_event("startup", {"message": "Service started"})
    This middleware logs each FastAPI request to Fluentd. It is initialized with an
    event tag, a FastAPI application, and the host and port of the Fluentd server.
    After initialization, it automatically logs each HTTP request's method, URL, and
    status code after the request is processed. In case of an exception during request
    processing, the traceback is logged as an error event.

    Additionally, it can be used to manually log custom events to Fluentd by calling
    the `log_event` method with an event tag and data dictionary.
    """

    def __init__(
        self,
        tag: str,
        app: FastAPI,
        fluentd_host: str,
        fluentd_port: int,
    ) -> None:
        super().__init__(tag, fluentd_host, fluentd_port)
        self.app = app

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[FastAPIResponse]],
    ) -> FastAPIResponse:
        response = FastAPIResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            self.log_event(
                "error",
                {
                    "method": request.method,
                    "url": str(request.url),
                    "traceback": "".join(
                        traceback.TracebackException.from_exception(exc).format(),
                    ),
                },
            )
        finally:
            if response is not None:
                self.log_event(
                    "request",
                    {
                        "method": request.method,
                        "url": str(request.url),
                        "status_code": response.status_code,
                    },
                )
        return response


class FluentLoggerFlaskMiddleware(BaseLogger):
    """
    Middleware to log Flask requests to Fluentd.

    Args:
        tag (str): Event tag
        app (Flask): Flask app
        fluentd_host (str): Fluentd host
        fluentd_port (int): Fluentd port

    Returns:
        None

    Usage:
        # Logging Flask requests
        app = Flask(__name__)
        FluentLoggerFlaskMiddleware("tag", app, fluentd_host, fluentd_port)

        # Logging application events
        logger = FluentLoggerFlaskMiddleware("tag", app, fluentd_host, fluentd_port)
        logger.log_event("startup", {"message": "Service started"})

    This middleware logs each Flask request to Fluentd. It is initialized with an event
    tag, a Flask application, and the host and port of the Fluentd server. After
    initialization, it automatically logs each HTTP request's method, URL, and status
    code after the request is processed.

    Additionally, it can be used to manually log custom events to Fluentd by calling
    the `log_event` method with an event tag and data dictionary.
    """

    def __init__(
        self,
        tag: str,
        app: Flask,
        fluentd_host: str,
        fluentd_port: int,
    ) -> None:
        super().__init__(tag, fluentd_host, fluentd_port)

        @app.after_request
        def log_request(response: FlaskResponse) -> FlaskResponse:
            self.log_event(
                "request",
                {
                    "method": request.method,
                    "url": request.url,
                    "status_code": response.status_code,
                },
            )
            return response

        @app.teardown_request
        def log_exception(exc: Exception | None) -> None:
            if exc is not None:
                self.log_event(
                    "error",
                    {
                        "method": request.method,
                        "url": request.url,
                        "traceback": "".join(
                            traceback.TracebackException.from_exception(exc).format(),
                        ),
                    },
                )
