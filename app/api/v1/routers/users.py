from fastapi.requests import Request
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.dependencies import get_db, get_current_user
from app.api.v1.services.user_service import user_service_v1
from app.api.v1.schemas.courses import CourseReadV1, CourseResponseV1
from app.api.v1.schemas.users import UserResponseV1, UserUpdateV1, UserReadV1


user_router_v1 = APIRouter()


@user_router_v1.get(
    "/users/me/",
    status_code=200,
    response_model=UserResponseV1,
    description="Get current user profile",
)
async def get_user_profile(
    request: Request,
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    user_profile: UserReadV1 = await user_service_v1.get_user_profile(
        curr_user, refresh_token, db
    )
    return UserResponseV1(
        message="User profile retrieved successfully", data=user_profile
    )


@user_router_v1.get(
    "/users/me/courses/",
    status_code=200,
    response_model=CourseResponseV1,
    description="Get current user courses",
)
async def get_user_courses(
    request: Request,
    page: int = Query(default=1, description="Set what page of course to view"),
    limit: int = Query(default=15, description="Set number of courses to view at once"),
    sort: str = Query(
        default=None, description="Sort courses by created_at and duration"
    ),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    user_courses: list[CourseReadV1] = await user_service_v1.get_user_courses(
        curr_user, refresh_token, db, sort, order, page, limit
    )
    return CourseResponseV1(
        message="User courses retrieved successfully", data=user_courses
    )


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
    refresh_token: str = request.cookies.get("refresh_token")
    user: UserReadV1 = await user_service_v1.update_user(
        curr_user, user_update, refresh_token, db
    )
    return UserResponseV1(message="User account updated successfully", data=user)
