"""Celery configuration for background task processing."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "basketball_reference_api",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.search.tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="US/Eastern",
    enable_utc=True,
    # Task execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=1800,  # 30 minutes max
    task_soft_time_limit=1500,  # 25 minutes soft limit
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    # Result backend
    result_expires=86400,  # 1 day
    # Rate limiting
    task_default_rate_limit="20/m",  # 20 tasks per minute
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Reindex search after weekly sync at 5am Sundays
    "weekly-search-reindex": {
        "task": "app.search.tasks.reindex_all",
        "schedule": {
            "minute": 0,
            "hour": 5,
            "day_of_week": 0,  # Sunday
        },
    },
}
