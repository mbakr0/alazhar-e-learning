
from app.domain.enum import CommonSubLevel, MainAcademicLevel, SpecializedLevel
from app.domain.models import SuggestionVideo
from app.schemas.video_info import VideoInfo


def suggestion_to_video_info(s: SuggestionVideo) -> VideoInfo:
    """Convert this dataclass to a Pydantic VideoInfo model"""
    return VideoInfo(
        video_id=s.video_id,
        main_level=MainAcademicLevel(s.main_level) if s.main_level else None,
        common_sub_level=CommonSubLevel(s.common_sub_level) if s.common_sub_level else None,
        specialized_level=SpecializedLevel(s.specialized_level) if s.specialized_level else None,
        lecture_title=s.lecture_title,
        lesson_name=s.lesson_name,
        is_related_video=s.is_related_video,
        batch=s.batch
    )