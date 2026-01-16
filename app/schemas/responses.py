from typing import List
from pydantic import BaseModel
from app.schemas.video_info import VideoInfo
class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: List[VideoInfo]

class ErrorResponse(BaseModel):
    success: bool
    message: str
