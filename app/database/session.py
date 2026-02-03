from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# async connection for api
# a connection pool is used to ensure connections are made available
async_engine: AsyncEngine = create_async_engine(
    url=settings.ASYNC_DB_URL,
    connect_args={"options": "-c timezone=utc"},
    pool_size=10,
    pool_timeout=10.0,
    pool_pre_ping=True,
    max_overflow=5,
)

async_db_session: AsyncSession = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, autocommit=False, autoflush=False
)


# sync connection for api
# a connection pool is used to ensure connections are made available
sync_engine: Engine = create_engine(
    url=settings.SYNC_DB_URL,
    connect_args={"options": "-c timezone=utc"},
    pool_size=10,
    pool_timeout=10.0,
    pool_pre_ping=True,
    max_overflow=5,
)


sync_db_session: Session = sessionmaker(
    bind=sync_engine, autocommit=False, autoflush=False
)
