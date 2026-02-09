from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


from app.core.config import settings
from app.tasks.celery_app import celery_app
from app.api.v1.services.auth_service import auth_service_v1
from app.api.v1.services.user_service import user_service_v1


db_engine: Engine = create_engine(
    url=settings.SYNC_DB_URL,
    pool_size=10,
    pool_timeout=10.0,
    pool_pre_ping=True,
    max_overflow=5,
    connect_args={"options": "-c timezone=utc"},
)


db_session: Session = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)

    
# background task to delete revoked or used refresh tokens
@celery_app.task
def delete_tokens():
    with db_session() as db:
        auth_service_v1.delete_refresh_tokens(db)


# background task to delete users permanently
@celery_app.task
def delete_users():
    with db_session() as db:
        user_service_v1.delete_user_accounts(db)
