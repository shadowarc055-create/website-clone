from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("osint", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
celery_app.conf.task_routes = {"app.queue.tasks.run_investigation": {"queue": "investigations"}}
