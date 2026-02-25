import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks_queue"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,          # keep results for 1 hour
    task_acks_late=True,          # ack only after task finishes (crash-safe)
    worker_prefetch_multiplier=1, # one task per worker at a time (fair dispatch)
    task_track_started=True,      # enables STARTED state in /status
)
