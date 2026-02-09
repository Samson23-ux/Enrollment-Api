from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, Sequence


from app.models.users import User
from app.models.courses import Course
from app.models.enrollments import Enrollment


class AdminRepo:
    async def get_all_students(
        self,
        db: AsyncSession,
        role_id: UUID,
        q: str | None,
        sort: str | None,
        order: str | None,
        offset: int,
        limit: int,
    ) -> Sequence[User]:
        sortable_fields: dict = {"created_at": Course.created_at}

        stmt = select(User).where(User.role_id == role_id)

        if q:
            stmt = stmt.where(User.name.ilike(q))

        stmt = stmt.offset(offset).limit(limit)

        if sort:
            sort = sortable_fields.get(sort, Course.created_at)
            if order == "desc":
                stmt = stmt.order_by(desc(sort))
            else:
                stmt = stmt.order_by(sort)

        res = await db.execute(stmt)
        students: Sequence[User] = res.scalars().all()

        return students
    
    async def get_all_instructors(
        self,
        db: AsyncSession,
        role_id: UUID,
        q: str | None,
        sort: str | None,
        order: str | None,
        offset: int,
        limit: int,
    ) -> Sequence[User]:
        sortable_fields: dict = {"created_at": Course.created_at}

        stmt = select(User).where(User.role_id == role_id)

        if q:
            stmt = stmt.where(User.name.ilike(q))

        stmt = stmt.offset(offset).limit(limit)

        if sort:
            sort = sortable_fields.get(sort, Course.created_at)
            if order == "desc":
                stmt = stmt.order_by(desc(sort))
            else:
                stmt = stmt.order_by(sort)

        res = await db.execute(stmt)
        instructors: Sequence[User] = res.scalars().all()

        return instructors
    
    async def get_all_enrollments(
        self,
        sort: str | None,
        order: str | None,
        offset: int,
        limit: int,
        db: AsyncSession,
    ) -> Sequence[Enrollment]:
        sortable_fields: dict = {"created_at": Course.created_at}

        stmt = select(Enrollment)

        stmt = stmt.offset(offset).limit(limit)

        if sort:
            sort = sortable_fields.get(sort, Course.created_at)
            if order == "desc":
                stmt = stmt.order_by(desc(sort))
            else:
                stmt = stmt.order_by(sort)

        res = await db.execute(stmt)
        enrollments: Sequence[Enrollment] = res.scalars().all()

        return enrollments


    async def get_course_enrollments(
        self,
        course_id: UUID,
        sort: str | None,
        order: str | None,
        offset: int,
        limit: int,
        db: AsyncSession,
    ) -> Sequence[Enrollment]:
        sortable_fields: dict = {"created_at": Course.created_at}

        stmt = select(Enrollment).where(Enrollment.course_id == course_id)

        stmt = stmt.offset(offset).limit(limit)

        if sort:
            sort = sortable_fields.get(sort, Course.created_at)
            if order == "desc":
                stmt = stmt.order_by(desc(sort))
            else:
                stmt = stmt.order_by(sort)

        res = await db.execute(stmt)
        enrollments: Sequence[Enrollment] = res.scalars().all()

        return enrollments


admin_repo_v1 = AdminRepo()
