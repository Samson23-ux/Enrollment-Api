from celery.app import Celery


from app.core.config import settings


celery_app = Celery(
    main="celery_app", broker=settings.BROKER_URL, include=["app.tasks.celery_tasks"]
)


celery_app.config_from_object("app.tasks.celeryconfig")


from app.tasks import celery_schedules
