from uuid import UUID
from fastapi.requests import Request
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.api.v1.schemas.users import UserRole
from app.dependencies import get_db, get_current_user, required_roles
from app.api.v1.schemas.courses import CourseCreateV1, CourseUpdateV1, CourseResponseV1


course_router_v1 = APIRouter()


@course_router_v1.get(
    "/courses/",
    status_code=200,
    response_model=CourseResponseV1,
    description="Get all active courses",
)
async def get_active_courses(
    request: Request,
    q: str = Query(default=None, description="Search for a course using its title"),
    page: int = Query(default=1, description="Set what page of course to view"),
    limit: int = Query(default=15, description="Set number of courses to view at once"),
    sort: str = Query(
        default=None, description="Sort courses by created_at and duration"
    ),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass


@course_router_v1.get(
    "/courses/{course_id}/",
    status_code=200,
    response_model=CourseResponseV1,
    description="Get course by id",
)
async def get_course_by_id(
    course_id: UUID,
    request: Request,
    curr_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pass


@course_router_v1.post(
    "/courses/",
    status_code=201,
    response_model=CourseResponseV1,
    description="Create a course",
)
async def create_course(
    request: Request,
    course_create: CourseCreateV1,
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@course_router_v1.patch(
    "/courses/{course_id}/",
    status_code=200,
    response_model=CourseResponseV1,
    description="Update a course",
)
async def update_course(
    course_id: UUID,
    request: Request,
    course_update: CourseUpdateV1,
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@course_router_v1.patch(
    "/courses/{course_id}/deactivate/",
    status_code=200,
    response_model=CourseResponseV1,
    description="Deactivate a course",
)
async def deactivate_course(
    course_id: UUID,
    request: Request,
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@course_router_v1.patch(
    "/courses/{course_id}/reactivate/",
    status_code=200,
    response_model=CourseResponseV1,
    description="Reactivate a course",
)
async def reactivate_course(
    course_id: UUID,
    request: Request,
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@course_router_v1.delete(
    "/courses/{course_id}/", status_code=204, description="Delete a course"
)
async def delete_course(
    course_id: UUID,
    request: Request,
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass
