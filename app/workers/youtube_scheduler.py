"""
Scheduled task to fetch YouTube videos daily.
"""
from datetime import datetime
from app.services.youtube_service import get_channel_videos
from app.domain.youtube import YouTubeVideo
from app.db.repo.videos_repo import insert_youtube_videos


def fetch_and_store_youtube_videos():
    """
    Fetch videos from YouTube channel and store them in database.
    This function is called by the scheduler once per day.
    """
    try:
        # Get videos from YouTube API
        video_tuples = get_channel_videos()
        
        # Convert to YouTubeVideo objects
        videos = []
        for video_tuple in video_tuples:
            video_id, title, published_at_str = video_tuple
            # Parse the datetime string
            published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
            videos.append(YouTubeVideo(
                video_id=video_id,
                title=title,
                published_at=published_at
            ))
        
        # Store in database
        insert_youtube_videos(videos)
        
        print(f"[{datetime.now()}] Successfully fetched and stored {len(videos)} videos")
        return len(videos)
    except Exception as e:
        print(f"[{datetime.now()}] Error fetching YouTube videos: {str(e)}")
        raise
