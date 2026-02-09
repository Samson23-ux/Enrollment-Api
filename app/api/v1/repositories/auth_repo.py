from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy import select, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.auth import RefreshToken
from app.api.v1.schemas.auth import TokenStatus


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

    def delete_refresh_tokens(self, db: Session):
        stmt = delete(RefreshToken).where(
            or_(
                RefreshToken.status == TokenStatus.REVOKED,
                RefreshToken.status == TokenStatus.USED,
                RefreshToken.expires_at <= datetime.now(timezone.utc),
            ),
        )

        db.execute(stmt)


auth_repo_v1 = AuthRepoV1()
