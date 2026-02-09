from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.users import User
from app.models.courses import Course
from app.models.enrollments import Enrollment


class EnrolRepoV1:
    async def get_enrollment(
        self, user_id: UUID, course_id: UUID, db: AsyncSession
    ) -> Enrollment | None:
        stmt = select(Enrollment).where(
            and_(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
        )

        res = await db.execute(stmt)
        enrollment: Enrollment | None = res.scalar()
        return enrollment
    
    async def create_enrollment(self, user: User, course: Course, db: AsyncSession):
        user.courses.append(course)
        await db.flush()
        await db.refresh(user)

    async def delete_enrollment(self, enrollment: Enrollment, db: AsyncSession):
        await db.delete(enrollment)
        await db.flush()


enrol_repo_v1 = EnrolRepoV1()
