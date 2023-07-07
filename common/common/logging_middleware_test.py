import io
import types
import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import FastAPI, Request
from flask import Flask
from .logging_middleware import (
    BaseLogger,
    FluentEventError,
    FluentLoggerFastAPIMiddleware,
    FluentLoggerFlaskMiddleware,
)
from fastapi.testclient import TestClient


def test_base_logger_emits_event():
    with patch("fluent.sender.setup") as mock_setup, patch(
        "fluent.event.Event"
    ) as mock_event:
        logger = BaseLogger("test", "localhost", 24224)
        logger.log_event("test_event", {"data": "test_data"})
        mock_setup.assert_called_once_with("test", host="localhost", port=24224)
        mock_event.assert_called_once_with("test_event", {"data": "test_data"})


def test_base_logger_handles_fluent_event_error():
    with patch("fluent.sender.setup"), patch(
        "fluent.event.Event",
        side_effect=FluentEventError(
            "test_event", {"data": "test_data"}, "Fluentd error"
        ),
    ), patch("sys.stderr", new=io.StringIO()) as fake_err:
        logger = BaseLogger("test", "localhost", 24224)
        logger.log_event("test_event", {"data": "test_data"})
        assert (
            "The logger middleware failed to send event to FluentD"
            in fake_err.getvalue()
        )


def test_base_logger_handles_generic_exception():
    with patch("fluent.sender.setup"), patch(
        "fluent.event.Event", side_effect=Exception("Generic error")
    ), patch("sys.stderr", new=io.StringIO()) as fake_err:
        logger = BaseLogger("test", "localhost", 24224)
        logger.log_event("test_event", {"data": "test_data"})
        assert (
            "The logger middleware experienced an unexpected error"
            in fake_err.getvalue()
        )


@pytest.mark.asyncio
async def test_fluent_logger_fastapi_middleware_emits_event():
    with patch("fluent.sender.setup") as mock_setup, patch(
        "fluent.event.Event"
    ) as mock_event:
        app = FastAPI()
        middleware = FluentLoggerFastAPIMiddleware("test", app, "localhost", 24224)
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "scheme": "http",
            "server": ("localhost", 80),
            "headers": [(b"host", b"localhost")],
        }
        request = Request(scope)
        call_next = AsyncMock(return_value=Mock(status_code=200))
        await middleware(request, call_next)

        mock_setup.assert_called_once_with("test", host="localhost", port=24224)
        mock_event.assert_called_once_with(
            "request",
            {"method": "GET", "url": "http://localhost/", "status_code": 200},
        )


def test_fluent_logger_fastapi_middleware_logs_errors():
    with patch("fluent.event.Event") as mock_event:
        app = FastAPI()
        error_message = "Test error"

        @app.get("/error")
        async def test_route():
            raise RuntimeError(error_message)

        middleware = FluentLoggerFastAPIMiddleware("test", app, "localhost", 24224)
        app.middleware("http")(middleware)

        client = TestClient(app)
        response = client.get("/error")
        assert response.status_code == 500

        # there should be two calls to mock_event,
        # one for the request and one for the error
        assert mock_event.call_count == 2

        error_call = mock_event.call_args_list[0]
        args, _ = error_call
        assert args[0] == "error"
        assert "Test error" in args[1]["traceback"]

        request_call = mock_event.call_args_list[1]
        args, _ = request_call
        assert args[0] == "request"
        assert args[1]["status_code"] == 500


def test_fluent_logger_flask_middleware_emits_event():
    with patch("fluent.sender.setup") as mock_setup, patch(
        "fluent.event.Event"
    ) as mock_event:
        app = Flask(__name__)
        middleware = FluentLoggerFlaskMiddleware("test", app, "localhost", 24224)

        @app.route("/")
        def test_route():
            return "Test"

        client = app.test_client()
        response = client.get("/")

        mock_setup.assert_called_once_with("test", host="localhost", port=24224)
        mock_event.assert_called_once_with(
            "request", {"method": "GET", "url": "http://localhost/", "status_code": 200}
        )


def test_fluent_logger_flask_middleware_logs_errors():
    with patch("fluent.event.Event") as mock_event:
        app = Flask(__name__)
        middleware = FluentLoggerFlaskMiddleware("test", app, "localhost", 24224)

        @app.route("/error")
        def test_route():
            raise RuntimeError("Test error")

        client = app.test_client()
        response = client.get("/error")
        assert response.status_code == 500

        mock_event.assert_called()

        args, _ = mock_event.call_args
        assert args[0] == "error"
        assert "Test error" in args[1]["traceback"]
