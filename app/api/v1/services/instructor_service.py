import sentry_sdk
from uuid import UUID
from sqlalchemy import Sequence
import sentry_sdk.logger as sentry_logger
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.users import User
from app.models.courses import Course
from app.core.security import validate_refresh_token
from app.api.v1.schemas.users import UserReadV1, UserReadBaseV1
from app.api.v1.schemas.courses import CourseReadV1, CourseReadBaseV1
from app.api.v1.repositories.instructor_repo import instructor_repo_v1
from app.core.exceptions import (
    ServerError,
    UsersNotFoundError,
    CoursesNotFoundError,
)


class InstructorService:
    async def get_instructor_courses(
        self,
        curr_user: User,
        refresh_token: str,
        db: AsyncSession,
        sort: str | None,
        order: str | None,
        page: int = 1,
        limit: int = 15,
    ) -> list[CourseReadV1]:
        _ = await validate_refresh_token(refresh_token, db)

        offset: int = (page * limit) - limit

        try:
            courses_db: Sequence[Course] = (
                await instructor_repo_v1.get_instructor_courses(
                    curr_user.id, db, sort, order, offset, limit
                )
            )

            if not courses_db:
                sentry_logger.error(
                    "Instructor {id} courses not found", id=curr_user.id
                )
                raise CoursesNotFoundError()

            user_courses: list[CourseReadV1] = []
            for course_db in courses_db:
                """a pagination has been applied which limits the number of courses
                to select, reducing the number of courses to iterate over"""
                course_read = CourseReadV1(
                    **CourseReadBaseV1.model_validate(course_db).model_dump(),
                    instructor=course_db.instructor.name
                )

                user_courses.append(course_read)

            sentry_logger.info(
                "Instructor {id} courses retrieved from database", id=curr_user.id
            )
            return user_courses
        except Exception as e:
            if isinstance(e, CoursesNotFoundError):
                raise CoursesNotFoundError()

            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while retrieving instructor {id}"
                "courses from database"
            )

            sentry_logger.error(
                error_message,
                id=curr_user.id,
            )
            raise ServerError() from e

    async def get_course_students(
        self,
        curr_user: User,
        course_id: UUID,
        refresh_token: str,
        db: AsyncSession,
        sort: str | None,
        order: str | None,
        page: int = 1,
        limit: int = 15,
    ):
        _ = await validate_refresh_token(refresh_token, db)

        offset = (page * limit) - limit

        try:
            course_students_db: Sequence[User] = (
                await instructor_repo_v1.get_course_students(
                    course_id, db, sort, order, offset, limit
                )
            )

            if not course_students_db:
                sentry_logger.error("Students not found for course {id}", id=course_id)
                raise UsersNotFoundError()
            
            course_students: list[UserReadV1] = []
            for course_student in course_students_db:
                user_read: UserReadV1 = UserReadV1(
                    **UserReadBaseV1.model_validate(course_student).model_dump(),
                    role=course_student.role.name
                )

                course_students.append(user_read)
            
            sentry_logger.info("Course {id} students retrieved from database", id=course_id)
            return course_students
        except Exception as e:
            if isinstance(e, UsersNotFoundError):
                raise UsersNotFoundError()

            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while retrieving course {id}"
                "students from database"
            )

            sentry_logger.error(
                error_message,
                id=course_id,
            )
            raise ServerError() from e


instructor_service_v1 = InstructorService()
