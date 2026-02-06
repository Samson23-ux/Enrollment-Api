from uuid import UUID
from fastapi import Depends
import sentry_sdk.logger as sentry_logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer


from app.models.users import User
from app.core.config import settings
from app.core.security import decode_token
from app.api.v1.schemas.users import UserRole
from app.database.session import async_db_session
from app.api.v1.services.user_service import user_service_v1
from app.core.exceptions import (
    AuthenticationError,
    UserNotFoundError,
    AuthorizationError,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/sign-in/")


async def get_db():
    try:
        session: AsyncSession = async_db_session()
        yield session
    finally:
        await session.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    key: str = settings.ACCESS_TOKEN_SECRET_KEY
    payload: dict = await decode_token(token, key)

    if not payload:
        sentry_logger.error("User not authenticated")
        raise AuthenticationError()

    user_id: UUID = payload.get("sub")

    user: User = await user_service_v1.get_user_by_id(user_id, db)

    if not user:
        sentry_logger.error("User {id} not found in database", id=user_id)
        raise UserNotFoundError()

    return user

def required_roles(roles: list[UserRole]):
    async def role_checker(curr_user: User = Depends(get_current_user)):
        if curr_user.role.name not in roles:
            sentry_logger.error("User {id} is not authorized", id=curr_user.id)
            raise AuthorizationError()
        return curr_user

    return role_checker
