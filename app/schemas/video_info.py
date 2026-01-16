from datetime import date
from pydantic import BaseModel

from app.domain.enum import CommonSubLevel, MainAcademicLevel, SpecializedLevel



class VideoInfo(BaseModel):
    video_id: str
    main_level: MainAcademicLevel | None = None
    common_sub_level : CommonSubLevel | None = None
    specialized_level : SpecializedLevel | None = None
    lecture_title : str | None = None
    lesson_name : str | None = None
    batch : date | None = None
    is_related_video:bool | None = None