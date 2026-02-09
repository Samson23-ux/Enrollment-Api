from fastapi.requests import Request
from fastapi.responses import JSONResponse


from app.main import app
from app.core.exceptions import (
    ServerError,
    AppException,
    create_handler,
    UserExistsError,
    CredentialError,
    EnrollmentError,
    CourseExistsError,
    UserNotFoundError,
    AuthorizationError,
    UsersNotFoundError,
    AuthenticationError,
    CourseNotFoundError,
    CoursesNotFoundError,
    EnrollmentExistsError,
    StudentsNotFoundError,
    InstructorNotFoundError,
    EnrollmentNotFoundError,
    InstructorsNotFoundError,
    EnrollmentsNotFoundError,
)


# exception for uncaught errors
@app.exception_handler(500)
async def server_error_handler(req: Request, exc: AppException):
    return JSONResponse(
        content={
            "error": "Internal server error",
            "message": "Oops! Somethings went wrong",
        }
    )


app.add_exception_handler(
    exc_class_or_status_code=ServerError,
    handler=create_handler(
        status_code=500,
        initial_detail={
            "error": "Internal server error",
            "message": "Oops! something went wrong",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=AuthenticationError,
    handler=create_handler(
        status_code=401,
        initial_detail={
            "error": "Authentication error",
            "message": "User is not authenticated",
            "resolution": "User should provide valid credentials for authentication",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=AuthorizationError,
    handler=create_handler(
        status_code=403,
        initial_detail={
            "error": "Authorization error",
            "message": "User is not authorized to make the requested action",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=UserNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "User not found",
            "message": "User not found with the id",
            "resolution": "Ensure the correct id is provided for the intended user",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=UsersNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "Users not found",
            "message": "No users found at the moment",
            "resolution": "Ensure the user is currently signed",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=EnrollmentsNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "Enrollments not found",
            "message": "No enrollments found at the moment",
            "resolution": "Ensure the user is currently signed",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=StudentsNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "Students not found",
            "message": "No students found at the moment",
            "resolution": "Ensure the user is currently signed",
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=InstructorNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "Instructor not found",
            "message": "The instructor provided does not exists",
            "resolution": "Ensure the correct instructor name is provided",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=InstructorsNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "Instructors not found",
            "message": "No instructors found at the moment",
            "resolution": "Ensure the user is currently signed",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=CoursesNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "Courses not found",
            "message": "No courses found at the moment",
            "resolution": (
                "Ensure the user is currently signed in or" "registered to a course"
            ),
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=CourseNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "Course not found",
            "message": "Course not found with the provided id",
            "resolution": "Ensure the id provided is valid and matches a course",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=EnrollmentNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "Enrollment not found",
            "message": "User is currently not enrolled for the course",
            "resolution": "Ensure the id provided is valid and matches a course",
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=UserExistsError,
    handler=create_handler(
        status_code=400,
        initial_detail={
            "error": "User exists",
            "message": "User already exists with the provided email",
            "resolution": (
                "Sign up with another email or sign in with the existing email"
            ),
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=CourseExistsError,
    handler=create_handler(
        status_code=400,
        initial_detail={
            "error": "Course exists",
            "message": "Course already exists with the provided course code",
            "resolution": (
                "Create course with another course code or check"
                "existing course activity"
            ),
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=EnrollmentExistsError,
    handler=create_handler(
        status_code=400,
        initial_detail={
            "error": "Enrollment exists",
            "message": "User already enrolled for course",
            "resolution": (
                "Ensure the provided course is the intended" "course for enrollment"
            ),
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=EnrollmentError,
    handler=create_handler(
        status_code=400,
        initial_detail={
            "error": "Enrollment error",
            "message": "Course is full",
            "resolution": (
                "Ensure the provided course is the intended" "course for enrollment"
            ),
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=CredentialError,
    handler=create_handler(
        status_code=400,
        initial_detail={
            "error": "Invalid credentials",
            "message": "User provided an invalid credentials for sign in",
            "resolution": "Check to confirm the provided credentials are correct",
        },
    ),
)
