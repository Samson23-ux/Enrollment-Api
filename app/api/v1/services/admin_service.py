import sentry_sdk
from uuid import UUID
from sqlalchemy import Sequence
import sentry_sdk.logger as sentry_logger
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.users import User, Role
from app.core.security import validate_refresh_token
from app.api.v1.schemas.enrollments import EnrollmentReadV1
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.repositories.admin_repo import admin_repo_v1
from app.api.v1.schemas.users import UserReadV1, UserReadBaseV1, UserRole
from app.core.exceptions import (
    ServerError,
    StudentsNotFoundError,
    InstructorsNotFoundError,
    EnrollmentsNotFoundError,
)


class AdminServiceV1:
    async def get_all_students(
        self,
        curr_user: User,
        refresh_token: str,
        db: AsyncSession,
        q: str | None,
        sort: str | None,
        order: str | None,
        page: int = 1,
        limit: int = 15,
    ) -> list[UserReadV1]:
        _ = await validate_refresh_token(refresh_token, db)

        offset: int = (page * limit) - limit

        try:
            user_role: Role = await user_service_v1.get_role(UserRole.STUDENT, db)

            students_db: Sequence[User] = await admin_repo_v1.get_all_students(
                db, user_role.id, q, sort, order, offset, limit
            )

            if not students_db:
                sentry_logger.error("Students not found")
                raise StudentsNotFoundError()

            students: list[UserReadV1] = []
            for student in students_db:
                user_read: UserReadV1 = UserReadV1(
                    **UserReadBaseV1.model_validate(student).model_dump(),
                    role=student.role.name
                )

                students.append(user_read)

            sentry_logger.info(
                "Students retrieved from database by admin {id}", id=curr_user.id
            )
            return students

        except Exception as e:
            if isinstance(e, StudentsNotFoundError):
                raise StudentsNotFoundError()

            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while retrieving"
                "students from database"
            )
            sentry_logger.error(error_message)
            raise ServerError() from e

    async def get_all_instructors(
        self,
        curr_user: User,
        refresh_token: str,
        db: AsyncSession,
        q: str | None,
        sort: str | None,
        order: str | None,
        page: int = 1,
        limit: int = 15,
    ) -> list[UserReadV1]:
        _ = await validate_refresh_token(refresh_token, db)

        offset: int = (page * limit) - limit

        try:
            user_role: Role = await user_service_v1.get_role(UserRole.INSTRUCTOR, db)

            instructors_db: Sequence[User] = await admin_repo_v1.get_all_instructors(
                db, user_role.id, q, sort, order, offset, limit
            )

            if not instructors_db:
                sentry_logger.error("Instructors not found")
                raise InstructorsNotFoundError()

            instructors: list[UserReadV1] = []
            for instructor in instructors_db:
                user_read: UserReadV1 = UserReadV1(
                    **UserReadBaseV1.model_validate(instructor).model_dump(),
                    role=instructor.role.name
                )

                instructors.append(user_read)

            sentry_logger.info(
                "Instructors retrieved from database by admin {id}", id=curr_user.id
            )
            return instructors

        except Exception as e:
            if isinstance(e, InstructorsNotFoundError):
                raise InstructorsNotFoundError()

            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while retrieving"
                "instructors from database"
            )
            sentry_logger.error(error_message)
            raise ServerError() from e

    async def get_all_enrollments(
        self,
        curr_user: User,
        refresh_token: str,
        db: AsyncSession,
        sort: str | None,
        order: str | None,
        page: int = 1,
        limit: int = 15,
    ) -> list[EnrollmentReadV1]:
        _ = await validate_refresh_token(refresh_token, db)

        offset: int = (page * limit) - limit

        try:
            enrollments_db: Sequence[User] = await admin_repo_v1.get_all_enrollments(
                sort, order, offset, limit, db
            )

            if not enrollments_db:
                sentry_logger.error("Enrollments not found")
                raise EnrollmentsNotFoundError()

            enrollments: list[EnrollmentReadV1] = []
            for enrollment in enrollments_db:
                enrol_read = EnrollmentReadV1(
                    course_title=enrollment.course.title,
                    course_code=enrollment.course.code,
                    course_duration=enrollment.course.duration,
                    created_at=enrollment.created_at,
                )

                enrollments.append(enrol_read)

                error_message = "Enrollments retrieved from database by admin {id}"
                sentry_logger.info(error_message, id=curr_user.id)
            return enrollments
        except Exception as e:
            if isinstance(e, EnrollmentsNotFoundError):
                raise EnrollmentsNotFoundError()

            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while retrieving"
                "Enrollments from database"
            )
            sentry_logger.error(error_message)
            raise ServerError() from e

    async def get_course_enrollments(
        self,
        curr_user: User,
        course_id: UUID,
        refresh_token: str,
        db: AsyncSession,
        sort: str | None,
        order: str | None,
        page: int = 1,
        limit: int = 15,
    ) -> list[EnrollmentReadV1]:
        _ = await validate_refresh_token(refresh_token, db)

        offset: int = (page * limit) - limit

        try:
            enrollments_db: Sequence[User] = await admin_repo_v1.get_course_enrollments(
                course_id, sort, order, offset, limit, db
            )

            if not enrollments_db:
                sentry_logger.error(
                    "Enrollments not found for course {id}", id=course_id
                )
                raise EnrollmentsNotFoundError()

            enrollments: list[EnrollmentReadV1] = []
            for enrollment in enrollments_db:
                enrol_read = EnrollmentReadV1(
                    course_title=enrollment.course.title,
                    course_code=enrollment.course.code,
                    course_duration=enrollment.course.duration,
                    created_at=enrollment.created_at,
                )

                enrollments.append(enrol_read)

                error_message = (
                    "Course {course_id} enrollments retrieved from database"
                    "by admin {admin_id}"
                )
                sentry_logger.info(
                    error_message, course_id=course_id, admin_id=curr_user.id
                )
            return enrollments
        except Exception as e:
            if isinstance(e, EnrollmentsNotFoundError):
                raise EnrollmentsNotFoundError()

            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while retrieving"
                "Course {id} enrollments from database"
            )
            sentry_logger.error(error_message, id=course_id)
            raise ServerError() from e

    async def assign_admin_role(
        self, curr_user: User, user_id: UUID, refresh_token: str, db: AsyncSession
    ) -> UserReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        user: User = await user_service_v1.get_user_by_id(user_id, db)

        user_role: Role = await user_service_v1.get_role(UserRole.ADMIN, db)

        try:
            user.role_id = user_role.id

            await user_service_v1.add_user(user, db)

            sentry_logger.info(
                "User {user_id} role updated to admin by admin {admin_id}",
                user_id=user_id, admin_id=curr_user.id
            )

            user_read: UserReadV1 = UserReadV1(
                    **UserReadBaseV1.model_validate(user).model_dump(),
                    role=user_role.name
            )

            await db.commit()
            return user_read
        except Exception as e:
            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while assigning admin role"
                "to user {user_id} by admin {admin_id}"
            )
            sentry_logger.error(error_message, user_id=user_id, admin_id=curr_user.id)
            raise ServerError() from e

    async def assign_instructor_role(
        self, curr_user: User, user_id: UUID, refresh_token: str, db: AsyncSession
    ) -> UserReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        user: User = await user_service_v1.get_user_by_id(user_id, db)

        user_role: Role = await user_service_v1.get_role(UserRole.INSTRUCTOR, db)

        try:
            user.role_id = user_role.id

            await user_service_v1.add_user(user, db)

            sentry_logger.info(
                "User {user_id} role updated to instructor by admin {admin_id}",
                user_id=user_id, admin_id=curr_user.id
            )

            user_read: UserReadV1 = UserReadV1(
                    **UserReadBaseV1.model_validate(user).model_dump(),
                    role=user_role.name
            )

            await db.commit()
            return user_read
        except Exception as e:
            sentry_sdk.capture_exception(e)

            error_message = (
                "Internal server error occured while assigning instructor role"
                "to user {user_id} by admin {admin_id}"
            )
            sentry_logger.error(error_message, user_id=user_id, admin_id=curr_user.id)
            raise ServerError() from e


admin_service_v1 = AdminServiceV1()
