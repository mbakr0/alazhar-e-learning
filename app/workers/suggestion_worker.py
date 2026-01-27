"""
Workers for suggestion and vote operations. All DB writes go through these jobs.
"""
from uuid import UUID
from app.db.repo.videos_repo import (
    create_title_suggestion,
    create_description_suggestion,
    vote_title_suggestion,
    vote_description_suggestion,
)
from app.domain.models import titleSuggestions, descriptionSuggestions


def job_create_title_suggestion(video_id: str, title_text: str) -> dict:
    """Create a title suggestion. Called from queue."""
    row = create_title_suggestion(video_id, title_text)
    return {
        "id": str(row.id),
        "video_id": row.video_id,
        "title_text": row.title_text,
        "approval_count": row.approval_count or 0,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def job_create_description_suggestion(video_id: str, description_text: str) -> dict:
    """Create a description suggestion. Called from queue."""
    row = create_description_suggestion(video_id, description_text)
    return {
        "id": str(row.id),
        "video_id": row.video_id,
        "description_text": row.description_text,
        "approval_count": row.approval_count or 0,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def job_vote_title_suggestion(suggestion_id: str, voter_hash: str) -> bool:
    """Vote on a title suggestion. Called from queue."""
    return vote_title_suggestion(UUID(suggestion_id), voter_hash)


def job_vote_description_suggestion(suggestion_id: str, voter_hash: str) -> bool:
    """Vote on a description suggestion. Called from queue."""
    return vote_description_suggestion(UUID(suggestion_id), voter_hash)


def job_create_lesson_name_suggestion(video_id: str, lesson_name_text: str) -> dict:
    """Create a lesson name suggestion. Called from queue."""
    from app.db.repo.videos_repo import create_lesson_name_suggestion
    row = create_lesson_name_suggestion(video_id, lesson_name_text)
    return {
        "id": str(row.id),
        "video_id": row.video_id,
        "lesson_name_text": row.lesson_name_text,
        "approval_count": row.approval_count or 0,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def job_create_lecturer_suggestion(video_id: str, lecturer_name_text: str) -> dict:
    """Create a lecturer name suggestion. Called from queue."""
    from app.db.repo.videos_repo import create_lecturer_suggestion
    row = create_lecturer_suggestion(video_id, lecturer_name_text)
    return {
        "id": str(row.id),
        "video_id": row.video_id,
        "lecturer_name_text": row.lecturer_name_text,
        "approval_count": row.approval_count or 0,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def job_vote_lesson_name_suggestion(suggestion_id: str, voter_hash: str) -> bool:
    """Vote on a lesson name suggestion. Called from queue."""
    from app.db.repo.videos_repo import vote_lesson_name_suggestion
    return vote_lesson_name_suggestion(UUID(suggestion_id), voter_hash)


def job_vote_lecturer_suggestion(suggestion_id: str, voter_hash: str) -> bool:
    """Vote on a lecturer suggestion. Called from queue."""
    from app.db.repo.videos_repo import vote_lecturer_suggestion
    return vote_lecturer_suggestion(UUID(suggestion_id), voter_hash)


def job_submit_related_vote(video_id: str, is_related: bool, voter_hash: str) -> bool:
    """Vote that a video is related or not. Ensures (video_id, is_related) row exists, then adds vote. Called from queue."""
    from app.db.repo.videos_repo import get_or_create_related_suggestion, vote_related_suggestion
    row = get_or_create_related_suggestion(video_id, is_related)
    return vote_related_suggestion(row.id, voter_hash)
