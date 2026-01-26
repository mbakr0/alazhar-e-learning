from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from uuid import UUID
from app.schemas.suggestions import (
    TitleSuggestionCreate,
    DescriptionSuggestionCreate,
    TitleSuggestionResponse,
    DescriptionSuggestionResponse,
    VoteRequest
)
from app.schemas.responses import SuccessResponse
from app.db.repo.videos_repo import (
    create_title_suggestion,
    create_description_suggestion,
    get_title_suggestions_by_video,
    get_description_suggestions_by_video,
    vote_title_suggestion,
    vote_description_suggestion
)
from app.domain.models import titleSuggestions, descriptionSuggestions
from fastapi_limiter.depends import RateLimiter

router = APIRouter()


def title_suggestion_to_response(ts: titleSuggestions) -> TitleSuggestionResponse:
    """Convert domain model to response schema."""
    return TitleSuggestionResponse(
        id=ts.id,
        video_id=ts.video_id,
        title_text=ts.title_text,
        approval_count=ts.approval_count or 0,
        created_at=ts.created_at
    )


def description_suggestion_to_response(ds: descriptionSuggestions) -> DescriptionSuggestionResponse:
    """Convert domain model to response schema."""
    return DescriptionSuggestionResponse(
        id=ds.id,
        video_id=ds.video_id,
        description_text=ds.description_text,
        approval_count=ds.approval_count or 0,
        created_at=ds.created_at
    )


@router.post(
    "/videos/{video_id}/title-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=20, minutes=1))]
)
async def create_title_suggestion_endpoint(
    video_id: str,
    suggestion: TitleSuggestionCreate
):
    """Create a new title suggestion for a video."""
    try:
        if suggestion.video_id != video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video ID in path must match video_id in body"
            )
        
        result = create_title_suggestion(suggestion.video_id, suggestion.title_text)
        return SuccessResponse(
            success=True,
            message="Title suggestion created successfully",
            data=title_suggestion_to_response(result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/videos/{video_id}/description-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=20, minutes=1))]
)
async def create_description_suggestion_endpoint(
    video_id: str,
    suggestion: DescriptionSuggestionCreate
):
    """Create a new description suggestion for a video."""
    try:
        if suggestion.video_id != video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video ID in path must match video_id in body"
            )
        
        result = create_description_suggestion(suggestion.video_id, suggestion.description_text)
        return SuccessResponse(
            success=True,
            message="Description suggestion created successfully",
            data=description_suggestion_to_response(result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/videos/{video_id}/title-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=30, minutes=1))]
)
async def get_title_suggestions(video_id: str):
    """Get all title suggestions for a video."""
    try:
        suggestions = get_title_suggestions_by_video(video_id)
        return SuccessResponse(
            success=True,
            message="Title suggestions fetched successfully",
            data=[title_suggestion_to_response(s) for s in suggestions]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/videos/{video_id}/description-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=30, minutes=1))]
)
async def get_description_suggestions(video_id: str):
    """Get all description suggestions for a video."""
    try:
        suggestions = get_description_suggestions_by_video(video_id)
        return SuccessResponse(
            success=True,
            message="Description suggestions fetched successfully",
            data=[description_suggestion_to_response(s) for s in suggestions]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/title-suggestions/{suggestion_id}/vote",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=50, minutes=1))]
)
async def vote_title_suggestion_endpoint(
    suggestion_id: UUID,
    vote: VoteRequest
):
    """Vote on a title suggestion."""
    try:
        voted = vote_title_suggestion(suggestion_id, vote.voter_hash)
        if not voted:
            return SuccessResponse(
                success=False,
                message="You have already voted on this suggestion",
                data=None
            )
        return SuccessResponse(
            success=True,
            message="Vote recorded successfully",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/description-suggestions/{suggestion_id}/vote",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=50, minutes=1))]
)
async def vote_description_suggestion_endpoint(
    suggestion_id: UUID,
    vote: VoteRequest
):
    """Vote on a description suggestion."""
    try:
        voted = vote_description_suggestion(suggestion_id, vote.voter_hash)
        if not voted:
            return SuccessResponse(
                success=False,
                message="You have already voted on this suggestion",
                data=None
            )
        return SuccessResponse(
            success=True,
            message="Vote recorded successfully",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
