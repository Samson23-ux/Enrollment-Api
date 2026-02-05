from fastapi.requests import Request
from fastapi.responses import JSONResponse


from app.main import app
from app.core.exceptions import (
    AppException,
    create_handler,
    UserNotFoundError,
    AuthorizationError,
    AuthenticationError,
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
    exc_class_or_status_code=AuthenticationError,
    handler=create_handler(
        status_code=401,
        initial_detail={
            "error": "Authentication error",
            "message": "User is not authenticated",
            "resolution": "User should provide valid credentials for authentication"
        }
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=AuthorizationError,
    handler=create_handler(
        status_code=403,
        initial_detail={
            "error": "Authorization error",
            "message": "User is not authorized to make the requested action"
        }
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=UserNotFoundError,
    handler=create_handler(
        status_code=404,
        initial_detail={
            "error": "User not found",
            "message": "User not found with the id",
            "resolution": "Ensure the correct id is provided for the intended user"
        },
    )
)
