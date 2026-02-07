import sentry_sdk
from uuid import UUID
from sqlalchemy import Row, Sequence
import sentry_sdk.logger as sentry_logger
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.courses import Course
from app.models.users import User, Role
from app.core.security import validate_refresh_token
from app.api.v1.schemas.courses import CourseReadV1
from app.api.v1.repositories.user_repo import user_repo_v1
from app.core.exceptions import ServerError, CoursesNotFoundError
from app.api.v1.schemas.users import UserReadBaseV1, UserReadV1, UserUpdateV1


class UserServiceV1:
    async def get_user_by_email(self, user_email: str, db: AsyncSession) -> Row | None:
        user: User | None = await user_repo_v1.get_user_by_email(user_email, db)
        return user

    async def get_role(self, role_name: str, db: AsyncSession) -> Role | None:
        role: Role | None = await user_repo_v1.get_role(role_name, db)
        return role

    async def get_user_by_id(self, user_id: UUID, db: AsyncSession):
        pass

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
                    instructor=course_db.instructor.name
                ).model_validate(course_db, extra="ignore")

                user_courses.append(course_read)

            sentry_logger.info(
                "User {id} courses retrieved from database", id=curr_user.id
            )
            return user_courses
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while retrieving user {id} courses",
                id=curr_user.id,
            )
            raise ServerError() from e

    async def add_user(self, user: User, db: AsyncSession):
        await user_repo_v1.add_user(user, db)

    async def update_user(
        self,
        curr_user: User,
        user_update: UserUpdateV1,
        refresh_token: str,
        db: AsyncSession,
    ) -> UserReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        user_update_dict: dict = user_update.model_dump(exclude_unset=True)

        for k, v in user_update_dict.items():
            setattr(curr_user, k, v)

        try:
            await user_repo_v1.add_user(curr_user, db)
            await db.commit()
            sentry_logger.info("User {id} account updated", id=curr_user.id)

            user_read: UserReadV1 = UserReadV1(
                **UserReadBaseV1.model_validate(curr_user).model_dump(),
                role=curr_user.role.name
            )
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


user_service_v1 = UserServiceV1()
