from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, Sequence


from app.models.courses import Course


class CourseRepoV1:
    async def get_courses(
        self,
        db: AsyncSession,
        q: str | None,
        sort: str | None,
        order: str | None,
        is_active: bool,
        offset: int,
        limit: int,
    ) -> Sequence[Course]:
        sortable_fields: dict = {
            "created_at": Course.created_at,
            "duration": Course.duration,
        }

        stmt = select(Course)

        if is_active is not None:
            if not isinstance(is_active, bool):
                is_active: bool = True

            stmt = stmt.where(Course.is_active.is_(is_active))

        if q:
            stmt = stmt.where(Course.title.ilike(q))

        stmt = stmt.offset(offset).limit(limit)

        if sort:
            sort = sortable_fields.get(sort, Course.created_at)
            if order == "desc":
                stmt = stmt.order_by(desc(sort))
            else:
                stmt = stmt.order_by(sort)

        res = await db.execute(stmt)
        active_courses: Sequence[Course] = res.scalars().all()

        return active_courses
    
    async def get_course_by_code(self, course_code: str, db: AsyncSession) -> Course | None:
        stmt = select(Course).where(Course.code == course_code)
        res = await db.execute(stmt)
        course: Course | None = res.scalar()
        return course
    
    async def get_course_by_id(self, course_id: UUID, db: AsyncSession) -> Course | None:
        stmt = select(Course).where(Course.id == course_id)
        res = await db.execute(stmt)
        course: Course | None = res.scalar()
        return course

    async def add_course(self, course: Course, db: AsyncSession):
        """create and update course"""
        db.add(course)
        await db.flush()
        await db.refresh(course)

    async def delete_course(self, course: Course, db: AsyncSession):
        """create and update course"""
        await db.delete(course)
        await db.flush()


course_repo_v1 = CourseRepoV1()
