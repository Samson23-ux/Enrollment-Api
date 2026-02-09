from uuid import UUID
from fastapi.requests import Request
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.users import User
from app.dependencies import get_db, required_roles
from app.api.v1.schemas.courses import CourseReadV1, CourseResponseV1
from app.api.v1.services.instructor_service import instructor_service_v1
from app.api.v1.schemas.users import UserRole, UserResponseV1, UserReadV1


instructor_router_v1 = APIRouter()


@instructor_router_v1.get(
    "/users/instructor/me/courses/",
    status_code=200,
    response_model=CourseResponseV1,
    description="Get the current instructor's courses",
)
async def get_instructor_courses(
    request: Request,
    page: int = Query(default=1, description="Set what page of course to view"),
    limit: int = Query(default=15, description="Set number of courses to view at once"),
    sort: str = Query(
        default=None, description="Sort courses by created_at and duration"
    ),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(required_roles([UserRole.INSTRUCTOR])),
    db: AsyncSession = Depends(get_db),
):

    refresh_token: str = request.cookies.get("refresh_token")
    user_courses: list[CourseReadV1] = await instructor_service_v1.get_instructor_courses(
        curr_user, refresh_token, db, sort, order, page, limit
    )
    return CourseResponseV1(message="Courses retrieved successfully", data=user_courses)


@instructor_router_v1.get(
    "/users/instructor/me/courses{course_id}/students/",
    status_code=200,
    response_model=UserResponseV1,
    description="Get students enrolled for the current instructor's course",
)
async def get_course_students(
    course_id: UUID,
    request: Request,
    page: int = Query(default=1, description="Set what page of course to view"),
    limit: int = Query(default=15, description="Set number of courses to view at once"),
    sort: str = Query(
        default=None, description="Sort courses by created_at and duration"
    ),
    order: str = Query(default=None, description="Sort in asc or desc"),
    curr_user: User = Depends(required_roles([UserRole.INSTRUCTOR])),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    students: list[UserReadV1] = await instructor_service_v1.get_course_students(
        curr_user, course_id, refresh_token, db, sort, order, page, limit
    )
    return UserResponseV1(message="Courses retrieved successfully", data=students)
