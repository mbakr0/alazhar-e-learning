from fastapi import APIRouter, HTTPException, status, Depends
from app.services.youtube_service import get_channel_video_count
from app.schemas.responses import SuccessResponse
from fastapi_limiter.depends import RateLimiter

router = APIRouter()


@router.get(
    "/youtube/count",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=10, minutes=1))]
)
async def get_youtube_video_count():
    """Get the total video count from YouTube channel."""
    try:
        count = get_channel_video_count()
        return SuccessResponse(
            success=True,
            message="Video count fetched successfully",
            data={"count": count}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
