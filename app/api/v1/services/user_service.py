import sentry_sdk
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import Row, Sequence
import sentry_sdk.logger as sentry_logger
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.courses import Course
from app.models.users import User, Role
from app.core.security import validate_refresh_token
from app.api.v1.repositories.user_repo import user_repo_v1
from app.api.v1.schemas.courses import CourseReadV1, CourseReadBaseV1
from app.api.v1.schemas.users import UserReadBaseV1, UserReadV1, UserUpdateV1, UserRole
from app.core.exceptions import (
    ServerError,
    CoursesNotFoundError,
    UserNotFoundError,
    UserExistsError,
)


class UserServiceV1:
    async def add_user(self, user: User, db: AsyncSession):
        """a method for other services to make use of"""
        await user_repo_v1.add_user(user, db)

    async def add_role(self, role: Role, db: AsyncSession):
        await user_repo_v1.add_role(role, db)

    async def get_user_by_email(self, user_email: str, db: AsyncSession) -> Row | None:
        user: User | None = await user_repo_v1.get_user_by_email(user_email, db)
        return user

    async def get_instructor_id(
        self, name: str, role_id: UUID, db: AsyncSession
    ) -> UUID | None:
        user_id: UUID | None = await user_repo_v1.get_instructor_id(name, role_id, db)
        return user_id

    async def get_deactivated_user(
        self, user_email: str, db: AsyncSession
    ) -> Row | None:
        user: User | None = await user_repo_v1.get_deactivated_user(user_email, db)
        return user

    async def get_role(self, role: UserRole, db: AsyncSession) -> Role | None:
        role: Role | None = await user_repo_v1.get_role(role, db)
        return role

    async def get_user_by_id(self, user_id: UUID, db: AsyncSession):
        user: User | None = await user_repo_v1.get_user_by_id(user_id, db)

        if not user:
            sentry_logger.error("User {id} not found in database", id=user_id)
            raise UserNotFoundError()

        return user

    async def get_user_profile(
        self, user: User, refresh_token: str, db: AsyncSession
    ) -> UserReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        user_read: UserReadV1 = UserReadV1(
            **UserReadBaseV1.model_validate(user).model_dump(), role=user.role.name
        )
        return user_read

    async def get_user_courses(
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

        # prevent negative or float numbers
        if page < 1 or not isinstance(page, int):
            page: int = 1
        
        if limit < 1 or not isinstance(limit, int):
            limit: int = 15

        offset: int = (page * limit) - limit

        try:
            courses_db: Sequence[Course] = await user_repo_v1.get_user_courses(
                curr_user.id, sort, order, offset, limit, db
            )

            if not courses_db:
                sentry_logger.error("Courses not found for user {id}", id=curr_user.id)
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
                "User {id} courses retrieved from database", id=curr_user.id
            )
            return user_courses
        except Exception as e:
            if isinstance(e, CoursesNotFoundError):
                raise CoursesNotFoundError()

            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while retrieving user {id} courses",
                id=curr_user.id,
            )
            raise ServerError() from e

    async def update_user(
        self,
        curr_user: User,
        user_update: UserUpdateV1,
        refresh_token: str,
        db: AsyncSession,
    ) -> UserReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        user_update_dict: dict = user_update.model_dump(exclude_unset=True)

        if user_update.email:
            user: User = await user_service_v1.get_user_by_email(user_update.email, db)

            if user:
                sentry_logger.error(
                    "User attempted to update account with an existing email {email}",
                    email=user.email,
                )
                raise UserExistsError()

        for k, v in user_update_dict.items():
            setattr(curr_user, k, v)

        try:
            await user_repo_v1.add_user(curr_user, db)

            sentry_logger.info("User {id} account updated", id=curr_user.id)

            user_read: UserReadV1 = UserReadV1(
                **UserReadBaseV1.model_validate(curr_user).model_dump(),
                role=curr_user.role.name
            )
            await db.commit()
            return user_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while updating user {id} account details",
                id=curr_user.id,
            )
            raise ServerError() from e

    async def delete_user(self, user: User, db: AsyncSession):
        await user_repo_v1.delete_user(user, db)

    def delete_user_accounts(self, db: Session):
        """deletes user accounts 30 days after deactivation"""
        try:
            user_repo_v1.delete_users(db)
            sentry_logger.info("User accounts deleted permanently")
            db.commit()
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error while deleting user accounts permanently"
            )
            raise ServerError() from e


user_service_v1 = UserServiceV1()
