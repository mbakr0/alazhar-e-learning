from fastapi import APIRouter, HTTPException, status
from typing import List
from app.mappers.video_mapper import suggestion_to_video_info
from app.queues.redis_queue import video_queue
from app.workers.video_worker import process_videos
from app.schemas.video_info import VideoInfo
from app.schemas.responses import SuccessResponse
from app.db.repo.videos_repo import get_all_suggest_videos
from fastapi import Depends
from fastapi_limiter.depends import RateLimiter

router = APIRouter()


@router.get("/")
async def root_api():
    return "Welcome to the API root"

# POST → Add videos
@router.post(
    "/videos",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=10, minutes=1))]
)
async def add_videos(videos: List[VideoInfo]):
    try:
        job = video_queue.enqueue(process_videos, videos)
        return SuccessResponse(
            success=True,
            message="Videos queued for insertion",
            data={
                "job_id": job.get_id()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# GET → Fetch videos
@router.get(
    "/videos",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK, 
    dependencies=[Depends(RateLimiter(times=10, minutes=1))]
)
async def fetch_videos():
    try:
        videos = get_all_suggest_videos()
        return SuccessResponse(
            success=True,
            message="Videos fetched successfully",
            data=[suggestion_to_video_info(video) for video in videos]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
