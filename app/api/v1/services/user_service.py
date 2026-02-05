from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession


class UserServiceV1:
    @staticmethod
    async def get_user_by_id(user_id: UUID, db: AsyncSession):
        pass


user_service_v1 = UserServiceV1()
