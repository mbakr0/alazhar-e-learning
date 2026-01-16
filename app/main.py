import subprocess
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes.videos import router as video_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    def run_worker():
        subprocess.call(["rq", "worker", "video_queue"])

    worker_thread = threading.Thread(
        target=run_worker,
        daemon=True
    )
    worker_thread.start()

    yield

app = FastAPI(lifespan=lifespan)
# routers
app.include_router(video_router, prefix="/api")

