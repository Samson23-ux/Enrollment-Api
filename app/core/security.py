import hashlib
import sentry_sdk
from uuid import uuid4
from typing import Optional
from jose import jwt, JWTError
from pwdlib import PasswordHash
import sentry_sdk.logger as sentry_logger
from pwdlib.hashers.argon2 import Argon2Hasher
from datetime import timedelta, datetime, timezone


from app.core.config import settings
from app.api.v1.schemas.auth import TokenDataV1


pws = PasswordHash(hashers=[Argon2Hasher()])


async def hash_password(password: str):
    password: str = password + settings.ARGON2_PEPPER
    return pws.hash(password)


async def hash_token(token: str):
    token_bytes: bytes = token.encode(encoding="utf-8")
    return hashlib.sha256(token_bytes).hexdigest()


async def verify_password(plain_password: str, password: str):
    plain_password: str = plain_password + settings.ARGON2_PEPPER
    return pws.verify(plain_password, password)


async def create_access_token(
    token_data: TokenDataV1, expire_time: Optional[datetime] = None
) -> str:
    if not expire_time:
        expire_time: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_TIME
        )
    else:
        expire_time: datetime = expire_time + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_TIME
        )

    payload: dict = {
        "sub": token_data.email,
        "exp": expire_time,
        "iat": datetime.now(timezone.utc),
    }

    token: str = jwt.encode(
        claims=payload,
        key=settings.ACCESS_TOKEN_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token


async def create_refresh_token(
    token_data: TokenDataV1, expire_time: Optional[datetime] = None
) -> str:
    if not expire_time:
        expire_time: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_TIME
        )
    else:
        expire_time: datetime = expire_time + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_TIME
        )

    payload: dict = {
        "sub": token_data.email,
        "exp": expire_time,
        "iat": datetime.now(timezone.utc),
        "jti": uuid4(),
    }

    token: str = jwt.encode(
        claims=payload,
        key=settings.REFRESH_TOKEN_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, payload["jti"]


async def decode_token(token: str, key: str):
    try:
        payload: dict = jwt.decode(
            token=token, key=key, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        sentry_logger.error("User provided an invalid token")
        sentry_sdk.capture_exception(e)
        return None
