from datetime import date
from typing import ClassVar
from enum import Enum
from pydantic import BaseModel

from app.domain.enum import CommonSubLevel, MainAcademicLevel, SpecializedLevel



class VideoInfo(BaseModel):
    video_id: str
    main_level: MainAcademicLevel
    common_sub_level : CommonSubLevel
    specialized_level : SpecializedLevel | None = None
    lecture_title : str
    lesson_name : str
    batch : date