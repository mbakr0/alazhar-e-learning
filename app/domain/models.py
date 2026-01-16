
from typing import ClassVar
from datetime import date
from datetime import datetime
from app.domain.enum import CommonSubLevel, MainAcademicLevel, SpecializedLevel
from dataclasses import dataclass


@dataclass
class SuggestionVideo:
    id: int| None = None
    created_at: datetime| None = None
    video_id: str | None = None
    main_level: MainAcademicLevel| None = None
    common_sub_level: CommonSubLevel | None = None
    specialized_level: SpecializedLevel | None = None
    lecture_title: str | None = None
    lesson_name: str| None = None
    batch: date | None = None

    columns: ClassVar[list[str]] = [
        "video_id",
        "main_level",
        "common_sub_level",
        "specialized_level",
        "lecture_title",
        "lesson_name",
        "batch"
    ]