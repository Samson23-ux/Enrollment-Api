from uuid import UUID
from fastapi.requests import Request
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.dependencies import get_db, required_roles
from app.api.v1.schemas.courses import CourseResponseV1
from app.api.v1.schemas.users import UserRole, UserResponseV1
from app.api.v1.schemas.enrollments import EnrollmentResponseV1


admin_router_v1 = APIRouter()


@admin_router_v1.get(
    "/admin/students/",
    status_code=200,
    response_model=UserResponseV1,
    description="Get all students on platform",
)
async def get_all_students(
    request: Request,
    page: int = Query(default=1, description="Set what page of student to view"),
    limit: int = Query(
        default=15, description="Set number of students to view at once"
    ),
    sort: str = Query(default=None, description="Sort students by created_at"),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@admin_router_v1.get(
    "/admin/courses/",
    status_code=200,
    response_model=UserResponseV1,
    description="Get all courses on platform",
)
async def get_all_courses(
    request: Request,
    page: int = Query(default=1, description="Set what page of course to view"),
    limit: int = Query(default=15, description="Set number of courses to view at once"),
    sort: str = Query(
        default=None, description="Sort courses by created_at and duration"
    ),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@admin_router_v1.get(
    "/admin/instructors/",
    status_code=200,
    response_model=UserResponseV1,
    description="Get all instructors on platform",
)
async def get_all_instructors(
    request: Request,
    page: int = Query(default=1, description="Set what page of instructor to view"),
    limit: int = Query(
        default=15, description="Set number of instructors to view at once"
    ),
    sort: str = Query(default=None, description="Sort instructors by created_at"),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@admin_router_v1.get(
    "/admin/enrollments/",
    status_code=200,
    response_model=EnrollmentResponseV1,
    description="Get all enrollments on platform",
)
async def get_all_enrollments(
    request: Request,
    page: int = Query(default=1, description="Set what page of enrollment to view"),
    limit: int = Query(
        default=15, description="Set number of enrollments to view at once"
    ),
    sort: str = Query(default=None, description="Sort enrollments by created_at"),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@admin_router_v1.get(
    "/admin/courses/{course_id}/enrollments/",
    status_code=200,
    response_model=EnrollmentResponseV1,
    description="Get all enrollments on platform",
)
async def get_course_enrollments(
    course_id: UUID,
    request: Request,
    page: int = Query(default=1, description="Set what page of enrollment to view"),
    limit: int = Query(
        default=15, description="Set number of enrollments to view at once"
    ),
    sort: str = Query(default=None, description="Sort enrollments by created_at"),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@admin_router_v1.patch(
    "/admin/users/{user_id}/assign-admin-role/",
    status_code=200,
    response_model=UserResponseV1,
    description="Assign admin role to a user",
)
async def assign_admin_role(
    user_id: UUID,
    request: Request,
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass


@admin_router_v1.patch(
    "/admin/users/{user_id}/assign-instructor-role/",
    status_code=200,
    response_model=UserResponseV1,
    description="Assign instructor role to a user",
)
async def assign_instructor_role(
    user_id: UUID,
    request: Request,
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    pass
