import pytest

from service.config import JWTConfig, ServiceConfig, get_jwt_config, get_service_config


def test_valid_config_object_created_when_jwt_secret_is_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JWT_SECRET", "test_secret")

    config = get_jwt_config()

    assert isinstance(config, JWTConfig)
    assert config.jwt_secret == "test_secret"  # noqa: S105
    assert config.jwt_algorithm == "HS256"


def test_exception_raised_when_jwt_secret_is_not_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValueError):
        get_jwt_config()


def test_exception_raised_when_invalid_jwt_algorithm_provied() -> None:
    with pytest.raises(ValueError):
        JWTConfig("test_secret", "invalid_algorithm")


def test_valid_service_config_object_created_when_url_is_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("USER_SERVICE_URL", "https://test.url")

    config = get_service_config()

    assert isinstance(config, ServiceConfig)
    assert config.user_service_url == "https://test.url"


def test_exception_raised_when_service_url_is_not_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("USER_SERVICE_URL", raising=False)

    with pytest.raises(ValueError):
        get_service_config()
