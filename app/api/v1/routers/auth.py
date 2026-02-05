from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm


from app.models.users import User
from app.api.v1.schemas.auth import TokenV1
from app.dependencies import get_db, get_current_user
from app.api.v1.schemas.users import UserResponseV1, UserCreateV1


auth_router_v1 = APIRouter()


@auth_router_v1.post(
    "/auth/sign-up/",
    status_code=201,
    response_model=UserResponseV1,
    description="Create user account",
)
async def sign_up(user_create: UserCreateV1, db: AsyncSession = Depends(get_db)):
    pass


@auth_router_v1.post(
    "/auth/sign-in/",
    status_code=201,
    response_model=TokenV1,
    description="Sign in with user credentials. Username field represent usere email",
)
async def sign_in(
    sign_in_form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    pass


@auth_router_v1.get(
    "/auth/refresh/",
    status_code=201,
    response_model=TokenV1,
    description="Get a new access token with a valid refresh token",
)
async def get_access_token(request: Request, db: AsyncSession = Depends(get_db)):
    pass


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
    pass


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
    pass


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
    pass


@auth_router_v1.delete(
    "/auth/deactivate/",
    status_code=204,
    description="Deactivate user account. Account will be deleted after 30 days",
)
async def deactivate_account(
    request: Request,
    email: str = Form(..., description="User email"),
    password: str = Form(..., description="Current password"),
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass


@auth_router_v1.delete(
    "/auth/delete-account/",
    status_code=204,
    description="Delete user account permanently",
)
async def delete_account(
    request: Request,
    email: str = Form(..., description="User email"),
    password: str = Form(..., description="Current password"),
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass
