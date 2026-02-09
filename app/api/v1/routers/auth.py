from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm


from app.models.users import User
from app.core.config import settings
from app.api.v1.schemas.auth import TokenV1
from app.dependencies import get_db, get_current_user
from app.api.v1.services.auth_service import auth_service_v1
from app.api.v1.schemas.users import UserResponseV1, UserCreateV1, UserReadV1


auth_router_v1 = APIRouter()


@auth_router_v1.post(
    "/auth/sign-up/",
    status_code=201,
    response_model=UserResponseV1,
    description="Create user account",
)
async def sign_up(user_create: UserCreateV1, db: AsyncSession = Depends(get_db)):
    user: UserReadV1 = await auth_service_v1.sign_up(user_create, db)
    return UserResponseV1(message="User created successfully", data=user)


@auth_router_v1.post(
    "/auth/sign-in/",
    status_code=201,
    response_model=TokenV1,
    description="Sign in with user credentials. Username field represent user email",
)
async def sign_in(
    response: Response,
    sign_in_form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    access_token, refresh_token = await auth_service_v1.sign_in(
        sign_in_form.username, sign_in_form.password, db
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        secure=settings.ENVIRONMENT.lower() == "production",
        samesite="lax",
    )
    return TokenV1(access_token=access_token)


@auth_router_v1.get(
    "/auth/refresh/",
    status_code=200,
    response_model=TokenV1,
    description="Get a new access token with a valid refresh token",
)
async def get_access_token(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    refresh_token: str = request.cookies.get("refresh_token")
    access_token, refresh_token = await auth_service_v1.create_new_token(
        refresh_token, db
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        secure=settings.ENVIRONMENT.lower() == "production",
        samesite="lax",
    )
    return TokenV1(access_token=access_token)


@auth_router_v1.patch(
    "/auth/update-password/",
    status_code=200,
    response_model=UserResponseV1,
    description="Update user password",
)
async def update_password(
    request: Request,
    curr_password: str = Form(..., description="Current password"),
    new_password: str = Form(..., description="New password"),
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    curr_user: UserReadV1 = await auth_service_v1.update_password(
        refresh_token, curr_password, new_password, curr_user, db
    )
    return UserResponseV1(message="User password updated successfully", data=curr_user)


@auth_router_v1.patch(
    "/auth/reset-password/",
    status_code=200,
    response_model=UserResponseV1,
    description="Reset user password",
)
async def reset_password(
    email: str = Form(..., description="User email"),
    new_password: str = Form(..., description="Current password"),
    db: AsyncSession = Depends(get_db),
):
    user: UserReadV1 = await auth_service_v1.reset_password(email, new_password, db)
    return UserResponseV1(message="User password reset successfully", data=user)


@auth_router_v1.patch(
    "/auth/reactivate/",
    status_code=200,
    response_model=UserResponseV1,
    description="Reactivate user account",
)
async def reactivate_account(
    email: str = Form(..., description="User email"),
    password: str = Form(..., description="Current password"),
    db: AsyncSession = Depends(get_db),
):
    user: UserReadV1 = await auth_service_v1.reactivate_account(email, password, db)
    return UserResponseV1(message="User account reactivated successfully", data=user)


@auth_router_v1.patch(
    "/auth/logout/",
    status_code=200,
    response_model=UserResponseV1,
    description="Logout",
)
async def logout_user(
    request: Request,
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    await auth_service_v1.logout(curr_user, refresh_token, db)
    return UserResponseV1(message="User logout successfully")


@auth_router_v1.delete(
    "/auth/deactivate/",
    status_code=204,
    description="Deactivate user account. Account will be deleted after 30 days",
)
async def deactivate_account(
    request: Request,
    password: str = Form(..., description="Current password"),
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    await auth_service_v1.deactivate_account(curr_user, password, refresh_token, db)


@auth_router_v1.delete(
    "/auth/delete-account/",
    status_code=204,
    description="Delete user account permanently",
)
async def delete_account(
    request: Request,
    password: str = Form(..., description="Current password"),
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    await auth_service_v1.delete_account(curr_user, password, refresh_token, db)
