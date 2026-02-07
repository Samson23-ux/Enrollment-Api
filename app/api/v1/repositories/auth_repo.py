from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.auth import RefreshToken


class AuthRepoV1:
    async def get_refresh_token(
        self, token_id: UUID, db: AsyncSession
    ) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.id == token_id)
        res = await db.execute(stmt)
        refresh_token: RefreshToken | None = res.scalar()
        return refresh_token

    async def add_token(self, refresh_token: RefreshToken, db: AsyncSession):
        db.add(refresh_token)
        await db.flush()
        await db.refresh(refresh_token)


auth_repo_v1 = AuthRepoV1()
