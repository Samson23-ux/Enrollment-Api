from uuid import UUID
from sqlalchemy import select, desc, Sequence
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.users import User
from app.models.courses import Course
from app.models.enrollments import Enrollment


class InstructorRepoV1:
    async def get_instructor_courses(
        self,
        instructor_id: UUID,
        db: AsyncSession,
        sort: str | None,
        order: str | None,
        offset: int,
        limit: int,
    ) -> Sequence[Course]:
        sortable_fields: dict = {
            "created_at": Course.created_at,
            "duration": Course.duration,
        }

        stmt = (
            select(Course)
            .join(User, Course.instructor_id == User.id)
            .where(Course.instructor_id == instructor_id)
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
        courses: Sequence[Course] = res.scalars().all()
        return courses

    async def get_course_students(
        self,
        course_id: UUID,
        db: AsyncSession,
        sort: str | None,
        order: str | None,
        offset: int,
        limit: int,
    ) -> Sequence[User]:
        sortable_fields: dict = {
            "created_at": Course.created_at,
            "duration": Course.duration,
        }

        stmt = (
            select(User)
            .select_from(Course)
            .join(Enrollment, Course.id == Enrollment.course_id)
            .join(User, User.id == Enrollment.user_id)
            .where(Course.id == course_id)
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
        students: Sequence[User] = res.scalars().all()
        return students


instructor_repo_v1 = InstructorRepoV1()
