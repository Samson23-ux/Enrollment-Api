import hashlib
import sentry_sdk
from typing import Optional
from uuid import uuid4, UUID
from jose import jwt, JWTError
from pwdlib import PasswordHash
import sentry_sdk.logger as sentry_logger
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime, timezone


from app.core.config import settings
from app.models.auth import RefreshToken
from app.core.exceptions import AuthenticationError
from app.api.v1.repositories.auth_repo import auth_repo_v1
from app.api.v1.schemas.auth import TokenDataV1, TokenStatus


pws = PasswordHash(hashers=[Argon2Hasher()])


async def hash_password(password: str):
    password: str = password + settings.ARGON2_PEPPER
    return pws.hash(password)


async def hash_token(token: str):
    token_bytes: bytes = token.encode(encoding="utf-8")
    return hashlib.sha256(token_bytes).hexdigest()


async def verify_password(plain_password: str, hashed_password: str):
    plain_password: str = plain_password + settings.ARGON2_PEPPER
    return pws.verify(plain_password, hashed_password)


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
        "sub": token_data.id,
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
) -> dict:
    if not expire_time:
        expire_time: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_TIME
        )
    else:
        expire_time: datetime = expire_time + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_TIME
        )

    payload: dict = {
        "sub": token_data.id,
        "exp": expire_time,
        "iat": datetime.now(timezone.utc),
        "jti": uuid4(),
    }

    token: str = jwt.encode(
        claims=payload,
        key=settings.REFRESH_TOKEN_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    data: dict = {
        "refresh_token": token,
        "token_id": payload["jti"],
        "expire_time": payload["exp"],
    }

    return data


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


async def prepare_tokens(user_id: UUID, token_data: TokenDataV1) -> dict:
    access_token: str = await create_access_token(token_data)

    refresh_token_data: dict = await create_refresh_token(token_data)

    token_id: UUID = refresh_token_data.get("token_id")
    refresh_token: str = refresh_token_data.get("refresh_token")
    expire_time: datetime = refresh_token_data.get("expire_time")

    refresh_token_db: RefreshToken = RefreshToken(
        id=token_id,
        token=await hash_token(refresh_token),
        user_id=user_id,
        expires_at=expire_time,
    )

    data: dict = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "refresh_token_db": refresh_token_db,
    }

    return data


async def validate_refresh_token(refresh_token: str, db: AsyncSession) -> RefreshToken:
    payload: dict | None = await decode_token(
        refresh_token, settings.REFRESH_TOKEN_SECRET_KEY
    )

    if not payload:
        sentry_logger.error("User not authenticated")
        raise AuthenticationError()

    token_id: UUID = payload.get("jti")

    refresh_token: RefreshToken | None = await auth_repo_v1.get_refresh_token(
        token_id, db
    )

    if (
        refresh_token.status == TokenStatus.REVOKED
        or refresh_token.status == TokenStatus.USED
    ):
        sentry_logger.error("User not authenticated")
        raise AuthenticationError()

    return refresh_token
