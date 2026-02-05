from sqlalchemy.ext.asyncio import AsyncSession


from app.api.v1.schemas.users import UserCreateV1, UserRole


class AuthServiceV1:
    @staticmethod
    async def create_role(role: UserRole, db: AsyncSession):
        pass


    @staticmethod
    async def create_admin(admin_create: UserCreateV1, db: AsyncSession):
        pass


    @staticmethod
    async def sign_up(user_create: UserCreateV1, db: AsyncSession):
        pass
        

auth_service_v1 = AuthServiceV1()
