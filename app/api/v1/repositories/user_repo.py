from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, Sequence

from app.models.courses import Course
from app.models.users import Role, User
from app.models.enrollments import Enrollment


class UserRepoV1:
    async def get_user_by_email(self, user_email: str, db: AsyncSession) -> User | None:
        stmt = select(User).where(
            and_(User.email == user_email, User.is_active.is_(True))
        )
        res = await db.execute(stmt)
        user: User | None = res.scalar()
        return user

    async def get_role(self, role_name, db: AsyncSession) -> Role | None:
        stmt = select(Role).where(func.lower(Role.name) == func.lower(role_name))
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
            .where(User.id == user_id)
        )

        stmt = stmt.offset(offset).limit(limit)

        if sort:
            if order == "desc":
                sort = sortable_fields.get(sort, Course.created_at)
                stmt = stmt.order_by(desc(sort))
            else:
                sort = sortable_fields.get(sort, Course.created_at)
                stmt = stmt.order_by(sort)

        user_courses = await db.execute(stmt)
        res: Sequence[Course] = user_courses.scalars().all()
        return res

    async def create_role(self, role: Role, db: AsyncSession):
        pass

    async def add_user(self, user: User, db: AsyncSession):
        """create and update user"""
        db.add(user)
        db.flush()
        await db.refresh(user)

    async def delete_user(self, user: User, db: AsyncSession):
        await db.delete(user)
        db.flush()


user_repo_v1 = UserRepoV1()
