from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, Sequence, delete


from app.models.courses import Course
from app.models.users import Role, User
from app.models.enrollments import Enrollment
from app.api.v1.schemas.users import UserRole


class UserRepoV1:
    async def get_user_by_email(self, user_email: str, db: AsyncSession) -> User | None:
        stmt = select(User).where(
            and_(User.email == user_email, User.is_active.is_(True))
        )
        res = await db.execute(stmt)
        user: User | None = res.scalar()
        return user

    async def get_instructor_id(
        self, name: str, role_id: UUID, db: AsyncSession
    ) -> UUID | None:
        stmt = select(User.id).where(
            and_(User.name == name, User.role_id == role_id, User.is_active.is_(True))
        )
        res = await db.execute(stmt)
        user_id: UUID | None = res.scalar()
        return user_id

    async def get_deactivated_user(
        self, user_email: str, db: AsyncSession
    ) -> User | None:
        stmt = select(User).where(User.email == user_email)
        res = await db.execute(stmt)
        user: User | None = res.scalar()
        return user

    async def get_user_by_id(self, user_id: UUID, db: AsyncSession) -> User | None:
        stmt = select(User).where(and_(User.id == user_id, User.is_active.is_(True)))
        res = await db.execute(stmt)
        user: User | None = res.scalar()
        return user

    async def get_role(self, role: UserRole, db: AsyncSession) -> Role | None:
        stmt = select(Role).where(Role.name == role)
        res = await db.execute(stmt)
        role: Role | None = res.scalar()
        return role

    async def get_user_courses(
        self,
        user_id: UUID,
        sort: str | None,
        order: str | None,
        offset: int,
        limit: int,
        db: AsyncSession,
    ) -> Sequence[Course]:
        sortable_fields: dict = {
            "created_at": Course.created_at,
            "duration": Course.duration,
        }

        stmt = (
            select(Course)
            .join(Enrollment, Course.id == Enrollment.course_id)
            .join(User, User.id == Enrollment.user_id)
            .where(and_(User.id == user_id, User.is_active.is_(True)))
            .offset(offset)
            .limit(limit)
        )

        if sort:
            sort = sortable_fields.get(sort, Course.created_at)
            if order == "desc":
                stmt = stmt.order_by(desc(sort))
            else:
                stmt = stmt.order_by(sort)

        res = await db.execute(stmt)
        user_courses: Sequence[Course] = res.scalars().all()
        return user_courses

    async def add_user(self, user: User, db: AsyncSession):
        """create and update user"""
        db.add(user)
        await db.flush()
        await db.refresh(user)

    async def add_role(self, role: Role, db: AsyncSession):
        """create and update role"""
        db.add(role)
        await db.flush()
        await db.refresh(role)

    async def delete_user(self, user: User, db: AsyncSession):
        """delete user permanently"""
        await db.delete(user)
        await db.flush()

    def delete_users(self, db: Session):
        """method for background task to delete users from db"""

        stmt = delete(User).where(User.delete_at <= datetime.now(timezone.utc))

        db.execute(stmt)


user_repo_v1 = UserRepoV1()
