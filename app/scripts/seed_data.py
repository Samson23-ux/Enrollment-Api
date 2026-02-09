"""Initialize database with roles and default admin"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


from app.core.config import settings
from app.database.session import async_engine
from app.api.v1.schemas.users import UserRole, UserCreateV1
from app.api.v1.services.auth_service import auth_service_v1


async_db_session: AsyncSession = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, autocommit=False, autoflush=False
)


async def seed_db():
    async def create_roles():
        roles: list[UserRole] = [UserRole.ADMIN, UserRole.STUDENT, UserRole.INSTRUCTOR]

        async_session: AsyncSession = async_db_session()

        try:
            await auth_service_v1.create_roles(roles, async_session)
        finally:
            await async_session.close()


    async def create_admin():
        admin_create: UserCreateV1 = UserCreateV1(
            name=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            nationality=settings.ADMIN_NATIONALITY,
            password=settings.ADMIN_PASSWORD
        )

        async_session: AsyncSession = async_db_session()

        try:
            await auth_service_v1.create_admin(admin_create, async_session)
        finally:
            await async_session.close()

    return await create_roles(), await create_admin()


if __name__ == "__main__":
    asyncio.run(seed_db())
