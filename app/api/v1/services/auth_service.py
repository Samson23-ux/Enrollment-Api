import sentry_sdk
from uuid import UUID
import sentry_sdk.logger as sentry_logger
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.users import Role, User
from app.models.auth import RefreshToken
from app.api.v1.repositories.auth_repo import auth_repo_v1
from app.api.v1.schemas.auth import TokenDataV1, TokenStatus
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.schemas.users import UserCreateV1, UserRole, UserReadBaseV1, UserReadV1
from app.core.exceptions import (
    UserExistsError,
    ServerError,
    CredentialError,
    UserNotFoundError,
)
from app.core.security import (
    hash_password,
    verify_password,
    prepare_tokens,
    validate_refresh_token,
)


class AuthServiceV1:
    async def get_tokens(self, user_id: UUID, db: AsyncSession) -> tuple[str]:
        token_data: TokenDataV1 = TokenDataV1(id=user_id)

        auth_token_data: dict = await prepare_tokens(user_id, token_data)

        try:
            refresh_token_db: str = auth_token_data.get("refresh_token_db")
            await auth_repo_v1.add_token(refresh_token_db, db)
            await db.commit()
            sentry_logger.info("Refresh token stored in database")
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while storing refresh token in database"
            )
            raise ServerError() from e

        access_token: str = auth_token_data.get("access_token")
        refresh_token: str = auth_token_data.get("refresh_token")

        return access_token, refresh_token

    async def inavlidate_token(
        self, refresh_token: RefreshToken, status: str, db: AsyncSession
    ):
        if status == TokenStatus.USED:
            refresh_token.status = status
        else:
            refresh_token.status = TokenStatus.REVOKED

        try:
            await auth_repo_v1.add_token(refresh_token, db)
            await db.commit()
            sentry_logger.info("Refresh token status updated")
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while updating refresh token status"
            )
            raise ServerError() from e

    async def create_role(self, role: UserRole, db: AsyncSession):
        pass

    async def create_admin(self, admin_create: UserCreateV1, db: AsyncSession):
        pass

    async def sign_up(self, user_create: UserCreateV1, db: AsyncSession) -> UserReadV1:
        """user is created with a student account initially then an admin updates role"""
        user: User = await user_service_v1.get_user_by_email(user_create.email, db)

        if user:
            sentry_logger.error(
                "User attempted to create an account with an existing email {email}",
                email=user.email,
            )
            raise UserExistsError()

        user_role: Role = await user_service_v1.get_role(UserRole.STUDENT, db)
        hashed_password: str = await hash_password(user_create.password)

        user_in_db: User = User(
            user_create.model_dump(exclude={"password"}),
            hashed_password=hashed_password,
            role_id=user_role.id,
        )

        try:
            await user_service_v1.add_user(user_in_db, db)
            await db.commit()
            sentry_logger.info(
                "User {id} account created successfully", id=user_in_db.id
            )

            user_read: UserReadV1 = UserReadV1(
                **UserReadBaseV1.model_validate(user_in_db).model_dump(),
                role=user_role.name
            )
            return user_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error("Internal server error occured while creating a user")
            raise ServerError() from e

    async def sign_in(self, email: str, password: str, db: AsyncSession) -> tuple[str]:
        user: User = await user_service_v1.get_user_by_email(email, db)

        if not user or not await verify_password(password, user.hashed_password):
            sentry_logger.error(
                "Invalid credentials provided for user {id}", email=user.id
            )
            raise CredentialError()

        auth_tokens: tuple[str] = await self.get_tokens(user.id, db)

        return auth_tokens

    async def create_new_token(
        self, refresh_token: str, db: AsyncSession
    ) -> tuple[str]:
        refresh_token: RefreshToken = await validate_refresh_token(refresh_token, db)

        await self.inavlidate_token(refresh_token, TokenStatus.USED, db)

        user_id: UUID = refresh_token.user_id

        auth_tokens: tuple[str] = await self.get_tokens(user_id, db)

        return auth_tokens

    async def update_password(
        self,
        refresh_token: str,
        curr_password: str,
        new_password: str,
        curr_user: User,
        db: AsyncSession,
    ) -> UserReadV1:
        _ = await validate_refresh_token(refresh_token, db)

        if not await verify_password(curr_password, curr_user.hashed_password):
            sentry_logger.error(
                "User {id} provided an invalid password", id=curr_user.id
            )
            raise CredentialError()

        try:
            curr_user.hashed_password = await hash_password(new_password)
            await user_service_v1.add_user(curr_user, db)
            await db.commit()
            sentry_logger.info("User {id} password updated", id=curr_user.id)

            user_read: UserReadV1 = UserReadV1(
                **UserReadBaseV1.model_validate(curr_user).model_dump(),
                role=curr_user.role.name
            )
            return user_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while updating user {id} password",
                id=curr_user.id,
            )
            raise ServerError() from e

    async def reset_password(
        self,
        email: str,
        new_password: str,
        db: AsyncSession,
    ) -> UserReadV1:
        user: User = await user_service_v1.get_user_by_email(email, db)

        if not user:
            sentry_logger.error("User not found with email {email}", email=email)
            raise UserNotFoundError()

        try:
            user.hashed_password = await hash_password(new_password)
            await user_service_v1.add_user(user, db)
            await db.commit()
            sentry_logger.info("User {id} password reset completed", id=user.id)

            user_read: UserReadV1 = UserReadV1(
                **UserReadBaseV1.model_validate(user).model_dump(),
                role=user.role.name
            )
            return user_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while resetting user {id} password",
                id=user.id,
            )
            raise ServerError() from e

    async def reactivate_account(
        self, email: str, password: str, db: AsyncSession
    ) -> UserReadV1:
        user: User = await user_service_v1.get_user_by_email(email, db)

        if not user or not await verify_password(password, user.hashed_password):
            sentry_logger.error(
                "Invalid credentials provided for user with email {email}", email=email
            )
            raise CredentialError()

        try:
            user.is_active = True
            await user_service_v1.add_user(user, db)
            await db.commit()
            sentry_logger.info("User {id} account reactivated", id=user.id)

            user_read: UserReadV1 = UserReadV1(
                **UserReadBaseV1.model_validate(user).model_dump(),
                role=user.role.name
            )
            return user_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while reactivating user {id} account",
                id=user.id,
            )
            raise ServerError() from e

    async def deactivate_account(
        self, curr_user: User, password: str, refresh_token: str, db: AsyncSession
    ):
        refresh_token: RefreshToken = await validate_refresh_token(refresh_token, db)

        if not await verify_password(password, curr_user.hashed_password):
            sentry_logger.error(
                "Invalid credentials provided for user {id}",
                id=curr_user.id,
            )
            raise CredentialError()

        try:
            curr_user.is_active = False
            await user_service_v1.add_user(curr_user, db)
            await db.commit()
            await self.inavlidate_token(refresh_token, TokenStatus.REVOKED, db)
            sentry_logger.info("User {id} account reactivated", id=curr_user.id)
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while deactivating user {id} account",
                id=curr_user.id,
            )
            raise ServerError() from e

    async def delete_account(
        self, curr_user: User, password: str, refresh_token: str, db: AsyncSession
    ):
        refresh_token: RefreshToken = await validate_refresh_token(refresh_token, db)

        if not await verify_password(password, curr_user.hashed_password):
            sentry_logger.error(
                "Invalid credentials provided for user {id}", id=curr_user.id
            )
            raise CredentialError()

        try:
            user_id = curr_user.id
            await user_service_v1.delete_user(curr_user, db)
            await db.commit()
            await self.inavlidate_token(refresh_token, TokenStatus.REVOKED, db)
            sentry_logger.info("User {id} account deleted", id=user_id)
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while deleting user {id} account",
                id=user_id,
            )
            raise ServerError() from e


auth_service_v1 = AuthServiceV1()
