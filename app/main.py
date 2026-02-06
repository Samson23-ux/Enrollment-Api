import sentry_sdk
from fastapi import Request, FastAPI
from datetime import datetime, timezone
import sentry_sdk.logger as sentry_logger


from app.core.config import settings
from app.api.v1.routers.auth import auth_router_v1
from app.api.v1.routers.users import user_router_v1
from app.api.v1.routers.admin import admin_router_v1
from app.api.v1.routers.courses import course_router_v1
from app.api.v1.routers.instructors import instructor_router_v1
from app.api.v1.routers.enrollments import enrollments_router_v1


sentry_sdk.init(
    dsn=settings.SENTRY_SDK_DSN,
    enable_logs=True,
    send_default_pii=True,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    profile_lifecycle="trace"
)


app = FastAPI(
    title=settings.API_NAME,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)


from app.core import exception_handlers


app.include_router(auth_router_v1, prefix=settings.API_PREFIX, tags=["Auth"])
app.include_router(user_router_v1, prefix=settings.API_PREFIX, tags=["Users"])
app.include_router(admin_router_v1, prefix=settings.API_PREFIX, tags=["Admin"])
app.include_router(course_router_v1, prefix=settings.API_PREFIX, tags=["Courses"])
app.include_router(instructor_router_v1, prefix=settings.API_PREFIX, tags=["Instructors"])
app.include_router(enrollments_router_v1, prefix=settings.API_PREFIX, tags=["Enrollments"])


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    req: str = f"{request.method} {request.url} {datetime.now(timezone.utc)}"
    sentry_logger.info(req)
    response = await call_next(request)
    response.headers['X-App-Name'] = 'Enrollment API'
    return response


@app.get("/api/v1/health", status_code=200, description="Check api health")
async def health_check():
    return {"Message": "OK"}
