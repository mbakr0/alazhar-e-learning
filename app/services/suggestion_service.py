from app.db.repo.videos_repo import get_suggest_videos
from domain.models import SuggestionVideo
from mappers.video_mapper import suggestion_to_video_info

def fetch_suggestion_videos(ids):
    suggestions = get_suggest_videos(ids)
    return [suggestion_to_video_info(s) for s in suggestions]