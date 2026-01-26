from app.domain.youtube import YouTubeVideo

def parse_youtube_item(item) -> YouTubeVideo:
    snippet = item["snippet"]

    return YouTubeVideo(
        video_id=snippet["resourceId"]["videoId"],
        title=snippet["title"],
        published_at=snippet["publishedAt"]
    )