import sentry_sdk
from fastapi import Request, FastAPI
from datetime import datetime, timezone
import sentry_sdk.logger as sentry_logger


from app.core.config import settings


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


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    req: str = f"{request.method} {request.url} {datetime.now(timezone.utc)}"
    sentry_logger.info(req)
    response = await call_next(request)
    response.headers['X-App-Name'] = 'Enrollment API'
    return response
