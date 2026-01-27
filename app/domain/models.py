
from typing import ClassVar
from datetime import datetime
from dataclasses import dataclass
import uuid


@dataclass
class videoInfo:
    video_id: str | None = None
    created_at: datetime| None = None
    title: str| None = None
    published_at: datetime| None = None
    is_related_video:bool | None = None
    
    columns: ClassVar[list[str]] = [
        "video_id",
        "created_at",
        "title",
        "published_at",
        "is_related_video"
    ]
@dataclass
class titleSuggestions:
    id: uuid.UUID | None = None
    video_id: str | None = None
    title_text: str| None = None
    approval_count: int| None = None
    created_at: datetime| None = None
    
    columns: ClassVar[list[str]] = [
        "id",
        "video_id",
        "title_text",
        "approval_count",
        "created_at"
    ]

@dataclass
class descriptionSuggestions:
    id: uuid.UUID | None = None
    video_id: str | None = None
    description_text: str| None = None
    approval_count: int| None = None
    created_at: datetime| None = None
    
    columns: ClassVar[list[str]] = [
        "id",
        "video_id",
        "description_text",
        "approval_count",
        "created_at"
    ]

@dataclass
class videoVotes:
    id: uuid.UUID | None = None
    video_id: str | None = None
    voter_hash: str| None = None
    created_at: datetime| None = None
    
    columns: ClassVar[list[str]] = [
        "id",
        "video_id",
        "voter_hash",
        "created_at"
    ]


@dataclass
class titleVotes:
    id: uuid.UUID | None = None
    title_suggestion_id: uuid.UUID | None = None
    voter_hash: str| None = None
    created_at: datetime| None = None
    
    columns: ClassVar[list[str]] = [
        "id",
        "title_suggestion_id",
        "voter_hash",
        "created_at"
    ]

@dataclass
class descriptionVotes:
    id: uuid.UUID | None = None
    description_suggestion_id: uuid.UUID | None = None
    voter_hash: str| None = None
    created_at: datetime| None = None
    
    columns: ClassVar[list[str]] = [
        "id",
        "description_suggestion_id",
        "voter_hash",
        "created_at"
    ]


@dataclass
class lessonNameSuggestions:
    id: uuid.UUID | None = None
    video_id: str | None = None
    lesson_name_text: str | None = None
    approval_count: int | None = None
    created_at: datetime | None = None

    columns: ClassVar[list[str]] = [
        "id", "video_id", "lesson_name_text", "approval_count", "created_at"
    ]


@dataclass
class lecturerSuggestions:
    id: uuid.UUID | None = None
    video_id: str | None = None
    lecturer_name_text: str | None = None
    approval_count: int | None = None
    created_at: datetime | None = None

    columns: ClassVar[list[str]] = [
        "id", "video_id", "lecturer_name_text", "approval_count", "created_at"
    ]


@dataclass
class relatedSuggestion:
    id: uuid.UUID | None = None
    video_id: str | None = None
    is_related: bool | None = None
    approval_count: int | None = None
    created_at: datetime | None = None

    columns: ClassVar[list[str]] = [
        "id", "video_id", "is_related", "approval_count", "created_at"
    ]


@dataclass
class SuggestionVideo:
    video_id: str | None = None
    main_level: str | None = None
    common_sub_level: str | None = None
    specialized_level: str | None = None
    lecture_title: str | None = None
    lesson_name: str | None = None
    batch: datetime | None = None
    is_related_video: bool | None = None
    
    columns: ClassVar[list[str]] = [
        "video_id",
        "main_level",
        "common_sub_level",
        "specialized_level",
        "lecture_title",
        "lesson_name",
        "batch",
        "is_related_video"
    ]