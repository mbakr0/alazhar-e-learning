from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class TitleSuggestionCreate(BaseModel):
    video_id: str
    title_text: str

class DescriptionSuggestionCreate(BaseModel):
    video_id: str
    description_text: str

class TitleSuggestionResponse(BaseModel):
    id: UUID
    video_id: str
    title_text: str
    approval_count: int
    created_at: datetime

class DescriptionSuggestionResponse(BaseModel):
    id: UUID
    video_id: str
    description_text: str
    approval_count: int
    created_at: datetime

class LessonNameSuggestionCreate(BaseModel):
    video_id: str
    lesson_name_text: str


class LecturerSuggestionCreate(BaseModel):
    video_id: str
    lecturer_name_text: str


class LessonNameSuggestionResponse(BaseModel):
    id: UUID
    video_id: str
    lesson_name_text: str
    approval_count: int
    created_at: datetime


class LecturerSuggestionResponse(BaseModel):
    id: UUID
    video_id: str
    lecturer_name_text: str
    approval_count: int
    created_at: datetime


class VoteRequest(BaseModel):
    voter_hash: str


class RelatedVoteRequest(BaseModel):
    is_related: bool
    voter_hash: str


class RelatedSuggestionResponse(BaseModel):
    id: UUID
    video_id: str
    is_related: bool
    approval_count: int
    created_at: datetime | None
