import pytest

from service.config import Config, get_config


def test_valid_config_object_created_when_jwt_secret_is_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JWT_SECRET", "test_secret")

    config = get_config()

    assert isinstance(config, Config)
    assert config.jwt_secret == "test_secret"  # noqa: S105
    assert config.jwt_algorithm == "HS256"


def test_exception_raised_when_jwt_secret_is_not_provided(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValueError) as excinfo:
        get_config()

    assert str(excinfo.value) == "JWT_SECRET and JWT_ALGORITHM must be set."


def test_exception_raised_when_invalid_jwt_algorithm_provied() -> None:
    with pytest.raises(ValueError):
        Config("test_secret", "invalid_algorithm")
