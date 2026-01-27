"""
User-facing suggestion APIs. All write operations (create, vote) go through the message queue.
Read operations (GET) hit the database directly.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from app.schemas.suggestions import (
    TitleSuggestionCreate,
    DescriptionSuggestionCreate,
    TitleSuggestionResponse,
    DescriptionSuggestionResponse,
    LessonNameSuggestionCreate,
    LecturerSuggestionCreate,
    LessonNameSuggestionResponse,
    LecturerSuggestionResponse,
    VoteRequest,
    RelatedVoteRequest,
    RelatedSuggestionResponse,
)
from app.schemas.responses import SuccessResponse
from app.queues.redis_queue import suggestions_queue
from app.workers.suggestion_worker import (
    job_create_title_suggestion,
    job_create_description_suggestion,
    job_vote_title_suggestion,
    job_vote_description_suggestion,
    job_create_lesson_name_suggestion,
    job_create_lecturer_suggestion,
    job_vote_lesson_name_suggestion,
    job_vote_lecturer_suggestion,
    job_submit_related_vote,
)
from app.db.repo.videos_repo import (
    get_title_suggestions_by_video,
    get_description_suggestions_by_video,
    get_lesson_name_suggestions_by_video,
    get_lecturer_suggestions_by_video,
    get_related_suggestions_by_video,
)
from app.domain.models import (
    titleSuggestions,
    descriptionSuggestions,
    lessonNameSuggestions,
    lecturerSuggestions,
    relatedSuggestion,
)
from fastapi_limiter.depends import RateLimiter

router = APIRouter()


def _title_to_resp(ts: titleSuggestions) -> TitleSuggestionResponse:
    return TitleSuggestionResponse(
        id=ts.id,
        video_id=ts.video_id,
        title_text=ts.title_text,
        approval_count=ts.approval_count or 0,
        created_at=ts.created_at,
    )


def _desc_to_resp(ds: descriptionSuggestions) -> DescriptionSuggestionResponse:
    return DescriptionSuggestionResponse(
        id=ds.id,
        video_id=ds.video_id,
        description_text=ds.description_text,
        approval_count=ds.approval_count or 0,
        created_at=ds.created_at,
    )


def _lesson_to_resp(ls: lessonNameSuggestions) -> LessonNameSuggestionResponse:
    return LessonNameSuggestionResponse(
        id=ls.id,
        video_id=ls.video_id,
        lesson_name_text=ls.lesson_name_text,
        approval_count=ls.approval_count or 0,
        created_at=ls.created_at,
    )


def _lecturer_to_resp(ls: lecturerSuggestions) -> LecturerSuggestionResponse:
    return LecturerSuggestionResponse(
        id=ls.id,
        video_id=ls.video_id,
        lecturer_name_text=ls.lecturer_name_text,
        approval_count=ls.approval_count or 0,
        created_at=ls.created_at,
    )


def _related_to_resp(r: relatedSuggestion) -> RelatedSuggestionResponse:
    return RelatedSuggestionResponse(
        id=r.id,
        video_id=r.video_id,
        is_related=r.is_related or False,
        approval_count=r.approval_count or 0,
        created_at=r.created_at,
    )


# ---- Title ----

@router.post(
    "/videos/{video_id}/title-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=20, minutes=1))],
)
async def create_title_suggestion_endpoint(video_id: str, suggestion: TitleSuggestionCreate):
    """Submit your own title suggestion (or vote on an existing one via /title-suggestions/{id}/vote). Queued."""
    if suggestion.video_id != video_id:
        raise HTTPException(status_code=400, detail="Video ID in path must match body")
    try:
        job = suggestions_queue.enqueue(
            job_create_title_suggestion,
            suggestion.video_id,
            suggestion.title_text,
        )
        return SuccessResponse(
            success=True,
            message="Title suggestion queued for processing",
            data={"job_id": job.get_id()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/videos/{video_id}/title-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=30, minutes=1))],
)
async def get_title_suggestions(video_id: str, limit: int = 5):
    """Top N title suggestions (default 5). User can vote on one of these or submit their own via POST."""
    suggestions = get_title_suggestions_by_video(video_id, limit=limit)
    return SuccessResponse(
        success=True,
        message="Title suggestions fetched successfully",
        data=[_title_to_resp(s) for s in suggestions],
    )


@router.post(
    "/title-suggestions/{suggestion_id}/vote",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=50, minutes=1))],
)
async def vote_title_suggestion_endpoint(suggestion_id: UUID, vote: VoteRequest):
    """Queue a vote on a title suggestion."""
    try:
        job = suggestions_queue.enqueue(
            job_vote_title_suggestion,
            str(suggestion_id),
            vote.voter_hash,
        )
        return SuccessResponse(
            success=True,
            message="Vote queued for processing",
            data={"job_id": job.get_id()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Description ----

@router.post(
    "/videos/{video_id}/description-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=20, minutes=1))],
)
async def create_description_suggestion_endpoint(video_id: str, suggestion: DescriptionSuggestionCreate):
    """Submit your own description (or vote on existing via /description-suggestions/{id}/vote). Queued."""
    if suggestion.video_id != video_id:
        raise HTTPException(status_code=400, detail="Video ID in path must match body")
    try:
        job = suggestions_queue.enqueue(
            job_create_description_suggestion,
            suggestion.video_id,
            suggestion.description_text,
        )
        return SuccessResponse(
            success=True,
            message="Description suggestion queued for processing",
            data={"job_id": job.get_id()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/videos/{video_id}/description-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=30, minutes=1))],
)
async def get_description_suggestions(video_id: str, limit: int = 5):
    """Top N description suggestions (default 5). Vote on one or submit your own via POST."""
    suggestions = get_description_suggestions_by_video(video_id, limit=limit)
    return SuccessResponse(
        success=True,
        message="Description suggestions fetched successfully",
        data=[_desc_to_resp(s) for s in suggestions],
    )


@router.post(
    "/description-suggestions/{suggestion_id}/vote",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=50, minutes=1))],
)
async def vote_description_suggestion_endpoint(suggestion_id: UUID, vote: VoteRequest):
    """Queue a vote on a description suggestion."""
    try:
        job = suggestions_queue.enqueue(
            job_vote_description_suggestion,
            str(suggestion_id),
            vote.voter_hash,
        )
        return SuccessResponse(
            success=True,
            message="Vote queued for processing",
            data={"job_id": job.get_id()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Lesson name ----

@router.post(
    "/videos/{video_id}/lesson-name-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=20, minutes=1))],
)
async def create_lesson_name_suggestion_endpoint(video_id: str, suggestion: LessonNameSuggestionCreate):
    """Submit your own lesson name (or vote on existing via /lesson-name-suggestions/{id}/vote). Queued."""
    if suggestion.video_id != video_id:
        raise HTTPException(status_code=400, detail="Video ID in path must match body")
    try:
        job = suggestions_queue.enqueue(
            job_create_lesson_name_suggestion,
            suggestion.video_id,
            suggestion.lesson_name_text,
        )
        return SuccessResponse(
            success=True,
            message="Lesson name suggestion queued for processing",
            data={"job_id": job.get_id()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/videos/{video_id}/lesson-name-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=30, minutes=1))],
)
async def get_lesson_name_suggestions(video_id: str, limit: int = 5):
    """Top N lesson name suggestions (default 5). Vote on one or submit your own via POST."""
    suggestions = get_lesson_name_suggestions_by_video(video_id, limit=limit)
    return SuccessResponse(
        success=True,
        message="Lesson name suggestions fetched successfully",
        data=[_lesson_to_resp(s) for s in suggestions],
    )


@router.post(
    "/lesson-name-suggestions/{suggestion_id}/vote",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=50, minutes=1))],
)
async def vote_lesson_name_suggestion_endpoint(suggestion_id: UUID, vote: VoteRequest):
    """Queue a vote on a lesson name suggestion."""
    try:
        job = suggestions_queue.enqueue(
            job_vote_lesson_name_suggestion,
            str(suggestion_id),
            vote.voter_hash,
        )
        return SuccessResponse(
            success=True,
            message="Vote queued for processing",
            data={"job_id": job.get_id()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Lecturer name ----

@router.post(
    "/videos/{video_id}/lecturer-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=20, minutes=1))],
)
async def create_lecturer_suggestion_endpoint(video_id: str, suggestion: LecturerSuggestionCreate):
    """Submit your own lecturer name (or vote on existing via /lecturer-suggestions/{id}/vote). Queued."""
    if suggestion.video_id != video_id:
        raise HTTPException(status_code=400, detail="Video ID in path must match body")
    try:
        job = suggestions_queue.enqueue(
            job_create_lecturer_suggestion,
            suggestion.video_id,
            suggestion.lecturer_name_text,
        )
        return SuccessResponse(
            success=True,
            message="Lecturer suggestion queued for processing",
            data={"job_id": job.get_id()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/videos/{video_id}/lecturer-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=30, minutes=1))],
)
async def get_lecturer_suggestions(video_id: str, limit: int = 5):
    """Top N lecturer suggestions (default 5). Vote on one or submit your own via POST."""
    suggestions = get_lecturer_suggestions_by_video(video_id, limit=limit)
    return SuccessResponse(
        success=True,
        message="Lecturer suggestions fetched successfully",
        data=[_lecturer_to_resp(s) for s in suggestions],
    )


@router.post(
    "/lecturer-suggestions/{suggestion_id}/vote",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=50, minutes=1))],
)
async def vote_lecturer_suggestion_endpoint(suggestion_id: UUID, vote: VoteRequest):
    """Queue a vote on a lecturer suggestion."""
    try:
        job = suggestions_queue.enqueue(
            job_vote_lecturer_suggestion,
            str(suggestion_id),
            vote.voter_hash,
        )
        return SuccessResponse(
            success=True,
            message="Vote queued for processing",
            data={"job_id": job.get_id()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Is related (users decide if the video is related or not) ----

@router.get(
    "/videos/{video_id}/related-suggestions",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=30, minutes=1))],
)
async def get_related_suggestions(video_id: str):
    """Returns the two options (related / not_related) and their vote counts. User votes to decide if the video is related."""
    suggestions = get_related_suggestions_by_video(video_id)
    return SuccessResponse(
        success=True,
        message="Related suggestions fetched successfully",
        data=[_related_to_resp(s) for s in suggestions],
    )


@router.post(
    "/videos/{video_id}/related-vote",
    response_model=SuccessResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=50, minutes=1))],
)
async def submit_related_vote(video_id: str, body: RelatedVoteRequest):
    """Vote whether this video is related or not. Queued. Use GET /videos?related_only=true to list only videos users marked as related."""
    try:
        job = suggestions_queue.enqueue(
            job_submit_related_vote,
            video_id,
            body.is_related,
            body.voter_hash,
        )
        return SuccessResponse(
            success=True,
            message="Related vote queued for processing",
            data={"job_id": job.get_id()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
