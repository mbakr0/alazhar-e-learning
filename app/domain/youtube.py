from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class YouTubeVideo:
    video_id: str
    title: str
    published_at: datetime