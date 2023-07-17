from datetime import datetime, timedelta, timezone

import jwt
from common.api.schemas.user import AuthToken, InternalUserIdentity
from fastapi import HTTPException, status

from service.config import JWTConfig


def create_token(
    data: dict,
    config: JWTConfig,
    expires_delta: timedelta = timedelta(minutes=30),
) -> AuthToken:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(tz=timezone.utc) + expires_delta})
    token = jwt.encode(to_encode, config.jwt_secret, algorithm=config.jwt_algorithm)
    return AuthToken(token=token)


def get_identity(
    token: str,
    secret: str,
    algorithm: str = "HS256",
) -> InternalUserIdentity:
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token: 'sub' claim missing",
            )
        return InternalUserIdentity(uuid=user_id)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
