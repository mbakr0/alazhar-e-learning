from fastapi import HTTPException
import googleapiclient.discovery
from core.config import YOUTUBE_API_KEY, PLAYLIST_ID, CHANNEL_ID

def get_youtube_client():
    return googleapiclient.discovery.build(
        "youtube", "v3", developerKey=YOUTUBE_API_KEY
    )

def get_channel_videos():
    if not YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="API key not set")
    try:
        youtube = get_youtube_client()
        next_page_token = None
        videos = []
        while True:
            request =  youtube.playlistItems().list(
                part="snippet",
                maxResults=50,
                playlistId=PLAYLIST_ID,
                pageToken=next_page_token
                )

            response = request.execute()

            for item in response.get("items", []):
                title = item["snippet"]["title"]
                publishedAt = item["snippet"]["publishedAt"]
                video_id = item["snippet"]["resourceId"]["videoId"]

                videos.append((
                     video_id,
                     title,
                    publishedAt,
                )) 
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return videos
    except googleapiclient.errors.HttpError as e:
        raise HTTPException(status_code=e.resp.status,detail=str(e))


     
def get_channel_video_count():
    if not YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="API key not set")
    try:
        youtube = get_youtube_client()
        response = youtube.channels().list(
            part="statistics",
            id=CHANNEL_ID  # You need to get the channel ID
        ).execute()
        
        count = int(response["items"][0]["statistics"]["videoCount"])
        return count
    except googleapiclient.errors.HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))