import subprocess
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from app.api.routes.videos import router as video_router
from app.core.config import REDIS_URL

from app.queues.redis_queue import redis_conn,video_queue

@asynccontextmanager
async def lifespan(app: FastAPI):
    def run_worker():
        subprocess.call(["rq", "worker", "video_queue"])

    worker_thread = threading.Thread(
        target=run_worker,
        daemon=True
    )
    worker_thread.start()
    await FastAPILimiter.init(redis_conn)
    yield

app = FastAPI(lifespan=lifespan)



# routers
@app.get("/")
async def root():
    return 'it\'s Working!'

# Root route for /api

app.include_router(video_router, prefix="/api")

