from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "pastebin",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.cleanup"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    result_expires=3600,  # 1 hour
)

celery_app.conf.beat_schedule = {
    "cleanup-expired-pastes-every-hour": {
        "task": "cleanup_expired_pastes",
        "schedule": crontab(minute=0),  # Every hour
    },
}
