import pytest
import pytest_asyncio
from sqlalchemy import text
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncTransaction,
)


from app.main import app
from app.database.base import Base
from app.dependencies import get_db
from app.core.config import settings
from app.api.v1.schemas.users import UserRole, UserCreateV1
from app.api.v1.services.auth_service import auth_service_v1
from tests.fake_data import fake_student, fake_admin, fake_course


@pytest_asyncio.fixture(scope="session")
async def get_async_engine():
    async_engine: AsyncEngine = create_async_engine(
        url=settings.ASYNC_DB_URL,
        pool_size=10,
        pool_pre_ping=True,
        pool_timeout=10.0,
        max_overflow=5,
    )

    async with async_engine.connect() as conn:
        # initialise db with required extensions
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))

    Base.metadata.create_all(bind=async_engine)

    yield async_engine

    async_engine.dispose()


@pytest_asyncio.fixture
async def get_async_session(get_async_engine):
    async_connection: AsyncConnection = get_async_engine.connect()
    async_transaction: AsyncTransaction = async_connection.begin()

    async_session: AsyncSession = async_sessionmaker(
        bind=async_connection,
        autocommit=False,
        autoflush=False,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session as session:
        yield session()

    await async_transaction.rollback()
    await async_connection.close()


@pytest_asyncio.fixture
async def test_client(get_async_session):
    # wrapper for the get async session function
    # fastapi dependencies are not invoked when passed into the Depends function
    async def test_get_db():
        yield get_async_session

    app.dependency_overrides[get_db] = test_get_db

    with TestClient() as client:
        yield client


@pytest_asyncio.fixture
async def create_role(get_async_session):
    await auth_service_v1.create_role(UserRole.ADMIN, get_async_session)
    await auth_service_v1.create_role(UserRole.STUDENT, get_async_session)
    await auth_service_v1.create_role(UserRole.INSTRUCTOR, get_async_session)


@pytest_asyncio.fixture
async def create_admin(create_role, get_async_session):
    admin_create: UserCreateV1 = UserCreateV1.model_validate(fake_admin)
    await auth_service_v1.create_admin(admin_create, get_async_session)


@pytest_asyncio.fixture
async def create_student(create_role, test_client):
    res = test_client.post("/api/v1/auth/sign-up/", json=fake_student)
    return res


@pytest_asyncio.fixture
async def create_course(test_client, create_admin):
    admin_email = fake_admin.get("email")
    admin_password = fake_admin.get("password")

    sign_in_res = test_client.post(
        "/api/v1/auth/sign-in/",
        data={"username": admin_email, "password": admin_password},
    )

    access_token = sign_in_res.json()["access_token"]

    res = test_client.post(
        "/api/v1/courses/", json=fake_course, headers={"Authorization": access_token}
    )
    return res
