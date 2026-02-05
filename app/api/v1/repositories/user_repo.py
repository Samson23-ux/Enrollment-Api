from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import Role, User


class UserRepoV1:
    @staticmethod
    async def create_role(role: Role, db: AsyncSession):
        pass


    @staticmethod
    async def add_user(user: User,  db: AsyncSession):
        '''create and update user'''
        pass


user_repo_v1 = UserRepoV1()
