# flake8: noqa: N805

import jwt
from pydantic import field_validator
from pydantic_settings import BaseSettings


class ServiceConfig(BaseSettings):
    user_service_url: str

    @field_validator("user_service_url")
    def validate_service_url(cls, v: str) -> str:
        if not v:
            msg = "USER_SERVICE_URL must be set."
            raise ValueError(msg)
        return v


class JWTConfig(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    @field_validator("jwt_algorithm")
    def validate_algorithm(cls, v: str) -> str:
        dummy_token = jwt.encode({"dummy": "payload"}, "secret")
        algorithms = jwt.get_unverified_header(dummy_token)["alg"]
        if v not in algorithms:
            msg = f"Invalid algorithm: {v}"
            raise ValueError(msg)
        return v

    @field_validator("jwt_secret")
    def validate_jwt_secret(cls, v: str) -> str:
        if not v:
            msg = "JWT_SECRET must be set."
            raise ValueError(msg)
        return v


# These mostly exist so that they can be mocked in fastapi route tests
def get_jwt_config() -> JWTConfig:
    return JWTConfig()


def get_service_config() -> ServiceConfig:
    return ServiceConfig()
