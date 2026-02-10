import sentry_sdk
from uuid import UUID
from sqlalchemy.orm import Session
import sentry_sdk.logger as sentry_logger
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta


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

        refresh_token_db: str = auth_token_data.get("refresh_token_db")
        await auth_repo_v1.add_token(refresh_token_db, db)

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

    async def create_roles(self, roles: list[UserRole], db: AsyncSession):
        for role in roles:
            user_role: Role = await user_service_v1.get_role(role, db)

            if not user_role:
                try:
                    role_db: Role = Role(name=role)
                    await user_service_v1.add_role(role_db, db)
                    await db.commit()
                    sentry_logger.info("Role {name} created", name=role.value)
                except Exception as e:
                    await db.rollback()
                    sentry_sdk.capture_exception(e)
                    sentry_logger.error(
                        "Internal server error occured while creating {name} role",
                        name=role.value,
                    )
                    raise ServerError() from e

    async def create_admin(self, admin_create: UserCreateV1, db: AsyncSession):
        user: User = await user_service_v1.get_user_by_email(admin_create.email, db)

        if not user:
            user_role: Role = await user_service_v1.get_role(UserRole.ADMIN, db)
            hashed_password: str = await hash_password(admin_create.password)

            admin_in_db: User = User(
                **admin_create.model_dump(exclude={"password"}),
                hashed_password=hashed_password,
                role_id=user_role.id,
            )

            try:
                await user_service_v1.add_user(admin_in_db, db)

                sentry_logger.info(
                    "Admin {id} account created successfully", id=admin_in_db.id
                )

                user_read: UserReadV1 = UserReadV1(
                    **UserReadBaseV1.model_validate(admin_in_db).model_dump(),
                    role=user_role.name
                )
                await db.commit()
                return user_read
            except Exception as e:
                await db.rollback()
                sentry_sdk.capture_exception(e)
                sentry_logger.error(
                    "Internal server error occured while creating admin"
                )
                raise ServerError() from e

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
            **user_create.model_dump(exclude={"password"}),
            hashed_password=hashed_password,
            role_id=user_role.id,
        )

        try:
            await user_service_v1.add_user(user_in_db, db)

            sentry_logger.info(
                "User {id} account created successfully", id=user_in_db.id
            )

            user_read: UserReadV1 = UserReadV1(
                **UserReadBaseV1.model_validate(user_in_db).model_dump(),
                role=user_role.name
            )
            await db.commit()
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
                "Invalid credentials provided for user {email}", email=email
            )
            raise CredentialError()

        try:
            auth_tokens: tuple[str] = await self.get_tokens(user.id, db)

            sentry_logger.info("User {id} signed in", id=user.id)

            await db.commit()
            return auth_tokens
        except Exception as e:
            print("HERE")
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while user {id} attempted to sign in",
                id=user.id,
            )
            raise ServerError() from e

    async def create_new_token(
        self, refresh_token: str, db: AsyncSession
    ) -> tuple[str]:
        refresh_token: RefreshToken = await validate_refresh_token(refresh_token, db)

        try:
            await self.inavlidate_token(refresh_token, TokenStatus.USED, db)

            refresh_token.used_at = datetime.now(timezone.utc)
            await auth_repo_v1.add_token(refresh_token, db)

            user_id: UUID = refresh_token.user_id
            auth_tokens: tuple[str] = await self.get_tokens(user_id, db)

            sentry_logger.info("Access token created")

            await db.commit()
            return auth_tokens
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while creating new access token"
            )
            raise ServerError() from e

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

            sentry_logger.info("User {id} password updated", id=curr_user.id)

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

            sentry_logger.info("User {id} password reset completed", id=user.id)

            user_read: UserReadV1 = UserReadV1(
                **UserReadBaseV1.model_validate(user).model_dump(),
                role=user.role.name
            )

            await db.commit()
            return user_read
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while resetting user {id} password",
                id=user.id,
            )
            raise ServerError() from e

    async def logout(
        self, curr_user: User, refresh_token: str, db: AsyncSession
    ):
        refresh_token: RefreshToken = await validate_refresh_token(refresh_token, db)

        try:
            await self.inavlidate_token(refresh_token, TokenStatus.REVOKED, db)
            refresh_token.revoked_at = datetime.now(timezone.utc)

            await auth_repo_v1.add_token(refresh_token, db)
            sentry_logger.info("User {id} logout", id=curr_user.id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while user {id} attempted to logout",
                id=curr_user.id,
            )
            raise ServerError() from e

    async def reactivate_account(
        self, email: str, password: str, db: AsyncSession
    ) -> UserReadV1:
        user: User = await user_service_v1.get_deactivated_user(email, db)

        if not user or not await verify_password(password, user.hashed_password):
            sentry_logger.error(
                "Invalid credentials provided for user with email {email}", email=email
            )
            raise CredentialError()

        try:
            user.is_active = True
            user.delete_at = None

            await user_service_v1.add_user(user, db)
            sentry_logger.info("User {id} account reactivated", id=user.id)

            user_read: UserReadV1 = UserReadV1(
                **UserReadBaseV1.model_validate(user).model_dump(),
                role=user.role.name
            )

            await db.commit()
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
            await self.inavlidate_token(refresh_token, TokenStatus.REVOKED, db)

            refresh_token.revoked_at = datetime.now(timezone.utc)
            await auth_repo_v1.add_token(refresh_token, db)

            curr_user.is_active = False
            curr_user.delete_at = datetime.now(timezone.utc) + timedelta(days=30)
            await user_service_v1.add_user(curr_user, db)

            sentry_logger.info("User {id} account reactivated", id=curr_user.id)
            await db.commit()
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
            await self.inavlidate_token(refresh_token, TokenStatus.REVOKED, db)

            refresh_token.revoked_at = datetime.now(timezone.utc)
            await auth_repo_v1.add_token(refresh_token, db)

            user_id = curr_user.id
            await user_service_v1.delete_user(curr_user, db)

            sentry_logger.info("User {id} account deleted", id=user_id)
            await db.commit()
        except Exception as e:
            await db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error(
                "Internal server error occured while deleting user {id} account",
                id=user_id,
            )
            raise ServerError() from e
        
    def delete_refresh_tokens(self, db: Session):
        try:
            auth_repo_v1.delete_refresh_tokens(db)
            sentry_logger.info('Refresh tokens deleted')
            db.commit()
        except Exception as e:
            db.rollback()
            sentry_sdk.capture_exception(e)
            sentry_logger.error('Internal server error while deleting refresh tokens')
            raise ServerError() from e


auth_service_v1 = AuthServiceV1()
