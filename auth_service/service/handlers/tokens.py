import datetime
from datetime import timedelta

import jwt
from fastapi import HTTPException, status


def create_token(
    data: dict,
    secret: str,
    algorithm: str,
    expires_delta: timedelta = timedelta(minutes=30),
) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, secret, algorithm=algorithm)


def verify_token(token: str, secret: str, algorithm: str) -> str:
    """Verifies an access token and returns the user's UUID if it's valid."""
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
