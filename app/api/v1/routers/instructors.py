from uuid import UUID
from fastapi.requests import Request
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.users import UserRole, UserResponseV1


from app.models.users import User
from app.dependencies import get_db, required_roles


instructor_router_v1 = APIRouter()


@instructor_router_v1.get(
    "/users/instructor/me/courses/",
    status_code=200,
    response_model="",
    description="Get the current instructor's courses",
)
async def get_instructor_courses(
    request: Request,
    curr_user: User = Depends(required_roles([UserRole.INSTRUCTOR])),
    db: AsyncSession = Depends(get_db),
):

    pass


@instructor_router_v1.get(
    "/users/instructor/me/courses{course_id}/students/",
    status_code=200,
    response_model=UserResponseV1,
    description="Get students enrolled for the current instructor's course",
)
async def get_course_students(
    course_id: UUID,
    request: Request,
    curr_user: User = Depends(required_roles([UserRole.INSTRUCTOR])),
    db: AsyncSession = Depends(get_db),
):
    pass
