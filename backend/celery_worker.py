from celery import Celery
import os
from database import engine, SessionLocal
from datetime import datetime

# Initialize Celery App
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
celery_app = Celery(
    "akasha_tasks",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Optional: Add Celery Beat schedule here if we don't want to use APScheduler inside FastAPI
celery_app.conf.beat_schedule = {
    'poll-rss-every-5-minutes': {
        'task': 'celery_worker.poll_rss_task',
        'schedule': 300.0,
    },
}

@celery_app.task
def poll_rss_task():
    """Fetches RSS feeds and triggers ingest tasks for new entries."""
    print(f"[{datetime.utcnow()}] Polling RSS Feeds...")
    from ingest_engine import IngestEngine
    engine = IngestEngine()
    
    # We can fetch goals from the DB directly here if needed
    try:
        memories = engine.fetch_latest_news()
        for memory in memories:
            # Enqueue the individual ingestion task
            ingest_memory_task.delay(memory)
    except Exception as e:
        print(f"Error polling RSS: {e}")

@celery_app.task
def ingest_memory_task(memory: dict):
    """Background task to ingest a memory using the heavy Akasha ingestion pipeline."""
    print(f"Ingesting memory: {memory['title']}")
    # We would run the async ingest_library_artifact here via an event loop, 
    # but since it's an async function we need to wrap it.
    import asyncio
    from main import ingest_library_artifact, pod_manager
    from database import SessionLocal
    
    db = SessionLocal()
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(
            ingest_library_artifact(
                title=memory["title"],
                content=memory["content"],
                artifact_type=memory["category"],
                extra_meta={"source_url": memory["link"]},
                db=db,
                user_id="system_user"
            )
        )
    except Exception as e:
        print(f"Failed to ingest memory via Celery: {e}")
    finally:
        db.close()
