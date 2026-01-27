import subprocess
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.api.routes.videos import router as video_router
from app.api.routes.suggestions import router as suggestions_router
from app.api.routes.youtube import router as youtube_router
from app.core.config import REDIS_URL
from app.workers.youtube_scheduler import fetch_and_store_youtube_videos

from app.queues.redis_queue import redis_conn, video_queue
import redis.asyncio as async_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    def run_worker():
        # Process both video jobs (internal) and suggestion/vote jobs (user writes via queue)
        subprocess.call(["rq", "worker", "video_queue", "suggestions_queue"])

    worker_thread = threading.Thread(
        target=run_worker,
        daemon=True
    )
    worker_thread.start()
    
    # Setup scheduler for daily YouTube video fetching
    scheduler = BackgroundScheduler()
    # Run daily at 2:00 AM UTC (adjust timezone as needed)
    scheduler.add_job(
        fetch_and_store_youtube_videos,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_youtube_fetch',
        name='Fetch YouTube videos daily',
        replace_existing=True
    )
    scheduler.start()
    
    async_redis_conn = async_redis.from_url(REDIS_URL)
    await FastAPILimiter.init(async_redis_conn)
    yield
    
    # Shutdown scheduler on app close
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)



# routers
@app.get("/")
async def root():
    return 'it\'s Working!'

# Root route for /api

app.include_router(video_router, prefix="/api")
app.include_router(suggestions_router, prefix="/api")
app.include_router(youtube_router, prefix="/api")

