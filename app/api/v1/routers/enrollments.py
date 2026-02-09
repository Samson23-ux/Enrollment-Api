from uuid import UUID
from fastapi.requests import Request
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.api.v1.schemas.users import UserRole
from app.dependencies import get_db, required_roles
from app.api.v1.services.enrol_service import enrol_service_v1
from app.api.v1.schemas.enrollments import EnrollmentResponseV1, EnrollmentReadV1


enrollments_router_v1 = APIRouter()


@enrollments_router_v1.post(
    "/courses/{course_id}/enrollments/",
    status_code=201,
    response_model=EnrollmentResponseV1,
    description="Enroll for a course",
)
async def create_enrollment(
    course_id: UUID,
    request: Request,
    curr_user: User = Depends(required_roles([UserRole.STUDENT])),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    course_enrol: EnrollmentReadV1 = await enrol_service_v1.create_enrollment(
        curr_user, course_id, refresh_token, db
    )
    return EnrollmentResponseV1(
        message="Course enrolled successfully", data=course_enrol
    )


@enrollments_router_v1.delete(
    "/courses/{course_id}/enrollments/",
    status_code=204,
    description="Unenroll for a course",
)
async def delete_enrollment(
    course_id: UUID,
    request: Request,
    curr_user: User = Depends(required_roles([UserRole.STUDENT])),
    db: AsyncSession = Depends(get_db),
):
    refresh_token: str = request.cookies.get("refresh_token")
    await enrol_service_v1.delete_enrollment(
        curr_user, course_id, refresh_token, db
    )
