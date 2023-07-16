import os

import jwt


class Config:
    def __init__(self, jwt_secret: str, jwt_algorithm: str = "HS256") -> None:
        if (
            jwt_algorithm
            not in jwt.get_unverified_header(jwt.encode({"some": "payload"}, "secret"))[
                "alg"
            ]
        ):
            msg = f"Invalid algorithm: {jwt_algorithm}"
            raise ValueError(msg)
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm

        if not all([self.jwt_secret, self.jwt_algorithm]):
            msg = "JWT_SECRET and JWT_ALGORITHM must be set."
            raise ValueError(msg)


# this mostly exists so that it can be mocked in fastapi route tests
def get_config() -> Config:
    jwt_secret = os.getenv("JWT_SECRET")

    return Config(jwt_secret)
