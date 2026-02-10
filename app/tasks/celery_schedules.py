from celery.schedules import crontab
from app.tasks.celery_app import celery_app


# schedule task to run periodically
celery_app.conf.beat_schedule = {
    "delete_tokens": {
        "task": "app.tasks.celery_tasks.delete_tokens",
        "schedule": crontab(hour=16, minute=0)
    },

    "delete_users": {
        "task": "app.tasks.celery_tasks.delete_users",
        "schedule": crontab(day_of_month=12, hour=14, minute=0)
    }
}
