# workers/video_worker.py
from typing import List
from app.schemas.video_info import VideoInfo
from app.db.repo.videos_repo import insert_suggestion_videos

def process_videos(videos: List[VideoInfo]):
    """
    videos: list of dicts
    """
    batch_size = 100
    for i in range(0, len(videos), batch_size):
        batch = videos[i:i+batch_size]
        insert_suggestion_videos(batch)