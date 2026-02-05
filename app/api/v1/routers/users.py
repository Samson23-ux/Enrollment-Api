from fastapi.requests import Request
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.dependencies import get_db, get_current_user
from app.api.v1.schemas.users import UserResponseV1, UserUpdateV1


user_router_v1 = APIRouter()


@user_router_v1.get(
    "/users/me/",
    status_code=200,
    response_model=UserResponseV1,
    description="Get current user profile",
)
async def get_user_profile(
    request: Request, curr_user: User = Depends(get_current_user)
):
    pass


@user_router_v1.get(
    "/users/me/courses/",
    status_code=200,
    response_model="",
    description="Get current user courses",
)
async def get_user_courses(
    request: Request,
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass


@user_router_v1.patch(
    "/users/me/",
    status_code=200,
    response_model=UserResponseV1,
    description="Update current user account",
)
async def update_user(
    request: Request,
    user_update: UserUpdateV1,
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass
