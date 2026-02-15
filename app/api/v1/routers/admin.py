from uuid import UUID
from fastapi.requests import Request
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.dependencies import get_db, required_roles
from app.api.v1.services.admin_service import admin_service_v1
from app.api.v1.schemas.enrollments import EnrollmentResponseV1
from app.api.v1.schemas.users import UserRole, UserResponseV1, UserReadV1


admin_router_v1 = APIRouter()


@admin_router_v1.get(
    "/admin/students/",
    status_code=200,
    response_model=UserResponseV1,
    description="Get all students on platform",
)
async def get_all_students(
    request: Request,
    q: str = Query(default=None, description="Search for a user using user's name"),
    page: int = Query(default=1, description="Set what page of student to view"),
    limit: int = Query(
        default=15, description="Set number of students to view at once"
    ),
    sort: str = Query(default=None, description="Sort students by created_at"),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    students: list[UserReadV1] = await admin_service_v1.get_all_students(
        curr_user, refresh_token, db, q, sort, order, page, limit
    )
    return UserResponseV1(message="Students retrieved successfully", data=students)


@admin_router_v1.get(
    "/admin/instructors/",
    status_code=200,
    response_model=UserResponseV1,
    description="Get all instructors on platform",
)
async def get_all_instructors(
    request: Request,
    q: str = Query(
        default=None, description="Search for an instructor using instructor's name"
    ),
    page: int = Query(default=1, description="Set what page of instructor to view"),
    limit: int = Query(
        default=15, description="Set number of instructors to view at once"
    ),
    sort: str = Query(default=None, description="Sort instructors by created_at"),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(required_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    instructors: list[UserReadV1] = await admin_service_v1.get_all_instructors(
        curr_user, refresh_token, db, q, sort, order, page, limit
    )
    return UserResponseV1(
        message="Instructors retrieved successfully", data=instructors
    )


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
    refresh_token: str = request.cookies.get("refresh_token")
    enrollments: list[UserReadV1] = await admin_service_v1.get_all_enrollments(
        curr_user, refresh_token, db, sort, order, page, limit
    )
    return EnrollmentResponseV1(
        message="Enrollments retrieved successfully", data=enrollments
    )


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
    refresh_token: str = request.cookies.get("refresh_token")
    enrollments: list[UserReadV1] = await admin_service_v1.get_course_enrollments(
        curr_user, course_id, refresh_token, db, sort, order, page, limit
    )
    return EnrollmentResponseV1(
        message="Enrollments retrieved successfully", data=enrollments
    )


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
    refresh_token: str = request.cookies.get("refresh_token")
    user: UserReadV1 = await admin_service_v1.assign_admin_role(
        curr_user, user_id, refresh_token, db
    )
    return UserResponseV1(message="Role updated successfully", data=user)


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
    refresh_token: str = request.cookies.get("refresh_token")
    user: UserReadV1 = await admin_service_v1.assign_instructor_role(
        curr_user, user_id, refresh_token, db
    )
    return UserResponseV1(message="Role updated successfully", data=user)
