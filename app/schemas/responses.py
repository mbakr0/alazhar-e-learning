from typing import List, Any
from pydantic import BaseModel
from app.schemas.video_info import VideoInfo

class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Any = None

class ErrorResponse(BaseModel):
    success: bool
    message: str
