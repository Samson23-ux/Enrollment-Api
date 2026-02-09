import sentry_sdk
from uuid import UUID
import sentry_sdk.logger as sentry_logger
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.users import User
from app.models.courses import Course
from app.models.enrollments import Enrollment
from app.core.security import validate_refresh_token
from app.api.v1.schemas.enrollments import EnrollmentReadV1
from app.api.v1.repositories.enrol_repo import enrol_repo_v1
from app.api.v1.services.course_service import course_service_v1
from app.core.exceptions import (
    ServerError,
    EnrollmentError,
    CourseNotFoundError,
    EnrollmentExistsError,
    EnrollmentNotFoundError,
)


class EnrolServiceV1:
    async def create_enrollment(
        self, curr_user: User, course_id: UUID, refresh_token: str, db: AsyncSession
    ) -> EnrollmentReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        course: Course | None = await course_service_v1.get_course(course_id, db)

        if not course:
            sentry_logger.error("Course not found with the id {id}", id=course_id)
            raise CourseNotFoundError()

        if course.capacity == course.total_students or course.is_active is False:
            sentry_logger.error("Course {id} is full", id=course_id)
            raise EnrollmentError()

        enrol_db: Enrollment | None = await enrol_repo_v1.get_enrollment(
            curr_user.id, course_id, db
        )

        if enrol_db:
            sentry_logger.error(
                "User {user_id} already enrolled for course {course_id}",
                user_id=curr_user.id,
                course_id=course_id,
            )
            raise EnrollmentExistsError()

        try:
            await enrol_repo_v1.create_enrollment(curr_user, course, db)

            course.total_students += 1

            # update course with the new total students
            await course_service_v1.add_course(course, db)

            enrol_db: Enrollment | None = await enrol_repo_v1.get_enrollment(
                curr_user.id, course_id, db
            )

            enrol_read: EnrollmentReadV1 = EnrollmentReadV1(
                course_title=course.title,
                course_code=course.code,
                course_duration=course.duration,
                created_at=enrol_db.created_at,
            )

            sentry_logger.info(
                "User {user_id} enrolled for course {course_id}",
                user_id=curr_user.id,
                course_id=course_id,
            )
            await db.commit()
            return enrol_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while enrolling user"
                "{user_id} for course {course_id}"
            )

            sentry_logger.error(
                error_message,
                user_id=curr_user.id,
                course_id=course_id,
            )
            raise ServerError() from e

    async def delete_enrollment(
        self, curr_user: User, course_id: UUID, refresh_token: str, db: AsyncSession
    ):
        _ = await validate_refresh_token(refresh_token, db)

        course: Course | None = await course_service_v1.get_course(course_id, db)

        if not course:
            sentry_logger.error("Course not found with the id {id}", id=course_id)
            raise CourseNotFoundError()

        enrol_db: Enrollment | None = await enrol_repo_v1.get_enrollment(
            curr_user.id, course_id, db
        )

        if not enrol_db:
            sentry_logger.error(
                "User {user_id} enrollment not found for course {course_id}",
                user_id=curr_user.id,
                course_id=course_id,
            )
            raise EnrollmentNotFoundError()

        try:
            await enrol_repo_v1.delete_enrollment(enrol_db, db)
            await db.commit()
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while deleting"
                "user {user_id} enrollment for course {course_id}"
            )

            sentry_logger.error(
                error_message,
                user_id=curr_user.id,
                course_id=course_id,
            )
            raise ServerError() from e


enrol_service_v1 = EnrolServiceV1()
