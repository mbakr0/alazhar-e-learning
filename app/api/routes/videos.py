from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.responses import SuccessResponse
from app.db.repo.videos_repo import get_videos_for_catalog
from fastapi_limiter.depends import RateLimiter

router = APIRouter()

# Videos are synced from YouTube daily. Users decide if each video is related (is_related) and suggest title, description, lesson name, lecturer name.


@router.get("/")
async def root_api():
    return "Welcome to the API root"


@router.get(
    "/videos",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=30, minutes=1))],
)
async def list_videos(related_only: bool = False):
    """List videos from the catalog. Use related_only=true to return only videos users have marked as related (related votes > not_related)."""
    try:
        videos = get_videos_for_catalog(related_only=related_only)
        return SuccessResponse(
            success=True,
            message="Videos fetched successfully",
            data=videos,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
