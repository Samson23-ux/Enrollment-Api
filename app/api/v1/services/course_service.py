import sentry_sdk
from uuid import UUID
from sqlalchemy import Sequence
import sentry_sdk.logger as sentry_logger
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.users import User
from app.models.courses import Course
from app.core.security import validate_refresh_token
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.repositories.course_repo import course_repo_v1
from app.api.v1.schemas.courses import (
    CourseCreateV1,
    CourseReadV1,
    CourseUpdateV1,
    CourseReadBaseV1,
)
from app.core.exceptions import (
    ServerError,
    CourseExistsError,
    CourseNotFoundError,
    CoursesNotFoundError,
    InstructorNotFoundError,
)


class CourseServiceV1:
    async def get_courses(
        self,
        refresh_token: str,
        db: AsyncSession,
        q: str | None,
        sort: str | None,
        order: str | None,
        is_active: bool = True,
        page: int = 1,
        limit: int = 15,
    ) -> list[CourseReadV1]:
        """to view only active courses, the is_active parameter is set to True"""
        _ = await validate_refresh_token(refresh_token, db)

        offset: int = (page * limit) - limit

        try:
            courses_db: Sequence[Course] = await course_repo_v1.get_courses(
                db, q, sort, order, is_active, offset, limit
            )

            if not courses_db:
                sentry_logger.error("Courses not found")
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

            sentry_logger.info("Courses retrieved from database")
            return user_courses
        except Exception as e:
            if isinstance(e, CoursesNotFoundError):
                raise CoursesNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while retrieving courses from database"
            )
            raise ServerError() from e

    async def get_course_by_id(
        self, course_id: UUID, refresh_token: str, db: AsyncSession
    ) -> CourseReadV1:
        _ = validate_refresh_token(refresh_token, db)

        try:
            course: Course | None = await course_repo_v1.get_course_by_id(course_id, db)

            if not course:
                sentry_logger.error("Course not found with the id {id}", id=course_id)
                raise CourseNotFoundError()

            course_read: CourseReadV1 = CourseReadV1(
                **CourseReadBaseV1.model_validate(course).model_dump(),
                instructor=course.instructor.name
            )

            sentry_logger.info("Course {id} retrieved from database", id=course_id)
            return course_read
        except Exception as e:
            if isinstance(e, CourseNotFoundError):
                raise CourseNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while retrieving course {id} from database",
                id=course_id,
            )
            raise ServerError() from e

    async def get_course(self, course_id: UUID, db: AsyncSession):
        course: Course | None = await course_repo_v1.get_course_by_id(course_id, db)
        return course

    async def add_course(self, course: Course, db: AsyncSession):
        """a method for other services to make use of"""
        await course_repo_v1.add_course(course, db)

    async def create_course(
        self,
        curr_user: User,
        course_create: CourseCreateV1,
        refresh_token: str,
        db: AsyncSession,
    ) -> CourseReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        course_with_code: Course | None = await course_repo_v1.get_course_by_code(
            course_create.code, db
        )

        if course_with_code:
            sentry_logger.error(
                "User {id} attempted to create an existing course", id=curr_user.id
            )
            raise CourseExistsError()

        instructor_id: UUID | None = await user_service_v1.get_user_id(
            course_create.instructor, db
        )

        if not instructor_id:
            sentry_logger.error(
                "Instructor for course {name} does not exists", db=course_create.title
            )
            InstructorNotFoundError()

        try:
            course_db: Course = Course(
                **course_create.model_dump(exclude={"instructor"}),
                instructor_id=instructor_id
            )
            course_id = course_db.id

            await course_repo_v1.add_course(course_db, db)

            sentry_logger.info("Course created by admin {id}", id=curr_user.id)

            course_read: CourseReadV1 = CourseReadV1(
                **CourseReadBaseV1.model_validate(course_db).model_dump(),
                instructor=course_db.instructor.name
            )

            await db.commit()
            return course_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while creating course {id}",
                id=course_id,
            )
            raise ServerError() from e

    async def update_course(
        self,
        curr_user: User,
        course_id: UUID,
        course_update: CourseUpdateV1,
        refresh_token: str,
        db: AsyncSession,
    ) -> CourseReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        course: Course | None = await course_repo_v1.get_course_by_id(course_id, db)

        if not course:
            sentry_logger.error("Course not found with the id {id}", id=course_id)
            raise CourseNotFoundError()

        if course_update.code:
            course_with_code: Course | None = await course_repo_v1.get_course_by_code(
                course_update.code, db
            )

            if course_with_code:
                sentry_logger.error(
                    "User {id} attempted to create an existing course", id=curr_user.id
                )
                raise CourseExistsError()

        if course_update.instructor:
            instructor_id: UUID | None = await user_service_v1.get_user_id(
                course_update.instructor, db
            )

            if not instructor_id:
                sentry_logger.error(
                    "Instructor for course {name} does not exists",
                    db=course_update.title,
                )
                InstructorNotFoundError()

        course_update_dict: dict = course_update.model_dump(exclude_unset=True)

        for k, v in course_update_dict.items():
            setattr(course, k, v)

        try:
            await course_repo_v1.add_course(course, db)

            course_read: CourseReadV1 = CourseReadV1(
                **CourseReadBaseV1.model_validate(course).model_dump(),
                instructor=course.instructor.name
            )
            await db.commit()
            sentry_logger.info(
                "Course {course_id} updated by admin {admin_id}",
                course_id=course_id,
                admin_id=curr_user.id,
            )
            return course_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while updating course {id}",
                id=course_id,
            )
            raise ServerError() from e

    async def reactivate_course(
        self, curr_user: User, course_id: UUID, refresh_token: str, db: AsyncSession
    ) -> CourseReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        course: Course | None = await course_repo_v1.get_course_by_id(course_id, db)

        if not course:
            sentry_logger.error("Course not found with the id {id}", id=course_id)
            raise CourseNotFoundError()

        try:
            course.is_active = True
            await course_repo_v1.add_course(course, db)

            course_read: CourseReadV1 = CourseReadV1(
                **CourseReadBaseV1.model_validate(course).model_dump(),
                instructor=course.instructor.name
            )
            await db.commit()
            sentry_logger.info(
                "Course {course_id} reactivated by admin {admin_id}",
                course_id=course_id,
                admin_id=curr_user.id,
            )
            return course_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while reactivating course {id}",
                id=course_id,
            )
            raise ServerError() from e

    async def deactivate_course(
        self, curr_user: User, course_id: UUID, refresh_token: str, db: AsyncSession
    ):
        _ = await validate_refresh_token(refresh_token, db)

        course: Course | None = await course_repo_v1.get_course_by_id(course_id, db)

        if not course:
            sentry_logger.error("Course not found with the id {id}", id=course_id)
            raise CourseNotFoundError()

        try:
            course.is_active = False
            await course_repo_v1.add_course(course, db)
            await db.commit()
            sentry_logger.info(
                "Course {course_id} deactivated by admin {admin_id}",
                course_id=course_id,
                admin_id=curr_user.id,
            )
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while deactivating course {id}",
                id=course_id,
            )
            raise ServerError() from e

    async def delete_course(
        self, curr_user: User, course_id: UUID, refresh_token: str, db: AsyncSession
    ):
        _ = await validate_refresh_token(refresh_token, db)

        course: Course | None = await course_repo_v1.get_course_by_id(course_id, db)

        if not course:
            sentry_logger.error("Course not found with the id {id}", id=course_id)
            raise CourseNotFoundError()

        try:
            await course_repo_v1.delete_course(course, db)
            await db.commit()
            sentry_logger.info(
                "Course {course_id} deleted by admin {admin_id}",
                course_id=course_id,
                admin_id=curr_user.id,
            )
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while deleting course {id}",
                id=course_id,
            )
            raise ServerError() from e


course_service_v1 = CourseServiceV1()
