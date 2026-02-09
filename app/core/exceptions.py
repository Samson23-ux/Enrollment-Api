# lazy evaluation of annotations
from __future__ import annotations
from fastapi.requests import Request
from datetime import datetime, timezone
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base class for app exception"""


class ServerError(AppException):
    """Internal server error"""

    pass


class AuthenticationError(AppException):
    """User not authenticated"""

    pass


class AuthorizationError(AppException):
    """User not authorized"""

    pass


class UserExistsError(AppException):
    """User already exists"""

    pass


class CourseExistsError(AppException):
    """Course already exists"""

    pass


class EnrollmentExistsError(AppException):
    """User already enrolled"""

    pass


class EnrollmentError(AppException):
    """Course is full"""

    pass


class EnrollmentNotFoundError(AppException):
    """User not enrolled"""

    pass


class EnrollmentsNotFoundError(AppException):
    """Enrollments not found"""

    pass


class UserNotFoundError(AppException):
    """User not found"""

    pass


class UsersNotFoundError(AppException):
    """Users not found"""

    pass


class StudentsNotFoundError(AppException):
    """Students not found"""

    pass


class InstructorNotFoundError(AppException):
    """Instructor not found"""

    pass


class InstructorsNotFoundError(AppException):
    """Instructors not found"""

    pass


class CoursesNotFoundError(AppException):
    """Courses not found"""

    pass


class CourseNotFoundError(AppException):
    """Course not found"""

    pass


class CredentialError(AppException):
    """Wrong credentials provided"""

    pass


def create_handler(
    status_code: int, initial_detail: dict
) -> callable[[Request, AppException], JSONResponse]:
    async def exception_handler(req: Request, exc: AppException):
        error_time: str = datetime.now(timezone.utc).isoformat()
        initial_detail["timestamp"] = error_time
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler
