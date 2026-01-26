# Alazhar E-Learning Project Summary

## Overview
This project is a FastAPI-based application that integrates with YouTube to fetch videos from a specific channel, store them in a Supabase (PostgreSQL) database, and allows users to suggest and vote on video titles and descriptions.

## Completed Features

### 1. Database Models & Domain Layer
- ✅ Fixed missing `SuggestionVideo` model in `app/domain/models.py`
- ✅ All domain models are properly defined:
  - `videoInfo` - Base video information
  - `titleSuggestions` - User suggestions for video titles
  - `descriptionSuggestions` - User suggestions for video descriptions
  - `titleVotes` - Votes on title suggestions
  - `descriptionVotes` - Votes on description suggestions
  - `videoVotes` - Votes on videos
  - `SuggestionVideo` - Video metadata for suggestions

### 2. Database Repository Functions
- ✅ Fixed typo in `get_videos_count()` (curser → cursor)
- ✅ Added repository functions for:
  - Creating title suggestions
  - Creating description suggestions
  - Fetching suggestions by video ID
  - Voting on title suggestions
  - Voting on description suggestions
  - All functions include proper error handling and transaction management

### 3. API Schemas
- ✅ Created `app/schemas/suggestions.py` with:
  - `TitleSuggestionCreate` - Request schema for creating title suggestions
  - `DescriptionSuggestionCreate` - Request schema for creating description suggestions
  - `TitleSuggestionResponse` - Response schema for title suggestions
  - `DescriptionSuggestionResponse` - Response schema for description suggestions
  - `VoteRequest` - Request schema for voting
- ✅ Updated `SuccessResponse` to be more flexible with `Any` type for data

### 4. API Routes

#### Video Routes (`/api/videos`)
- ✅ `GET /api/videos` - Fetch all suggestion videos
- ✅ `POST /api/videos` - Add videos (queued for processing)

#### Suggestions Routes (`/api/videos/{video_id}/...`)
- ✅ `POST /api/videos/{video_id}/title-suggestions` - Create a title suggestion
- ✅ `POST /api/videos/{video_id}/description-suggestions` - Create a description suggestion
- ✅ `GET /api/videos/{video_id}/title-suggestions` - Get all title suggestions for a video
- ✅ `GET /api/videos/{video_id}/description-suggestions` - Get all description suggestions for a video
- ✅ `POST /api/title-suggestions/{suggestion_id}/vote` - Vote on a title suggestion
- ✅ `POST /api/description-suggestions/{suggestion_id}/vote` - Vote on a description suggestion

#### YouTube Routes (`/api/youtube`)
- ✅ `GET /api/youtube/count` - Get total video count from YouTube channel
- ⚠️ Video fetching is now automated - runs daily at 2:00 AM UTC via scheduled task

### 5. Fixed Issues
- ✅ Fixed import paths throughout the codebase
- ✅ Fixed Redis connection to use sync Redis for RQ (async Redis for FastAPILimiter)
- ✅ Fixed worker to properly handle VideoInfo objects
- ✅ Fixed video route to properly enqueue videos
- ✅ Removed debug print statements

### 6. Rate Limiting
All endpoints are protected with rate limiting:
- Video operations: 10 requests/minute
- Suggestion creation: 20 requests/minute
- Suggestion fetching: 30 requests/minute
- Voting: 50 requests/minute
- YouTube fetching: 5 requests/minute

## Database Schema Requirements

The following tables are expected in your Supabase database:

### `video_info`
- `video_id` (PRIMARY KEY, TEXT)
- `title` (TEXT)
- `published_at` (TIMESTAMP)
- `created_at` (TIMESTAMP, default: now())

### `suggestion_video_info`
- `video_id` (PRIMARY KEY, TEXT)
- `main_level` (TEXT, nullable)
- `common_sub_level` (TEXT, nullable)
- `specialized_level` (TEXT, nullable)
- `lecture_title` (TEXT, nullable)
- `lesson_name` (TEXT, nullable)
- `batch` (DATE, nullable)
- `is_related_video` (BOOLEAN, nullable)

### `title_suggestions`
- `id` (PRIMARY KEY, UUID, default: uuid_generate_v4())
- `video_id` (TEXT, FOREIGN KEY to video_info)
- `title_text` (TEXT)
- `approval_count` (INTEGER, default: 0)
- `created_at` (TIMESTAMP, default: now())

### `description_suggestions`
- `id` (PRIMARY KEY, UUID, default: uuid_generate_v4())
- `video_id` (TEXT, FOREIGN KEY to video_info)
- `description_text` (TEXT)
- `approval_count` (INTEGER, default: 0)
- `created_at` (TIMESTAMP, default: now())

### `title_votes`
- `id` (PRIMARY KEY, UUID, default: uuid_generate_v4())
- `title_suggestion_id` (UUID, FOREIGN KEY to title_suggestions)
- `voter_hash` (TEXT)
- `created_at` (TIMESTAMP, default: now())
- UNIQUE constraint on (title_suggestion_id, voter_hash)

### `description_votes`
- `id` (PRIMARY KEY, UUID, default: uuid_generate_v4())
- `description_suggestion_id` (UUID, FOREIGN KEY to description_suggestions)
- `voter_hash` (TEXT)
- `created_at` (TIMESTAMP, default: now())
- UNIQUE constraint on (description_suggestion_id, voter_hash)

### `video_votes`
- `id` (PRIMARY KEY, UUID, default: uuid_generate_v4())
- `video_id` (TEXT, FOREIGN KEY to video_info)
- `voter_hash` (TEXT)
- `created_at` (TIMESTAMP, default: now())

## Environment Variables Required

Create a `.env` file with:
```
USER=your_db_user
PASSWORD=your_db_password
HOST=your_db_host
PORT=your_db_port
DATABASE_Name=your_database_name
YOUTUBE_API_KEY=your_youtube_api_key
REDIS_URL=your_redis_url
```

## How to Use

1. **YouTube Video Fetching**: 
   - Videos are automatically fetched from the YouTube channel once per day at 2:00 AM UTC
   - The scheduled task runs in the background and stores new videos in the `video_info` table
   - No manual intervention is required - the system handles this automatically

2. **Create Suggestions**:
   - Users can create title suggestions: `POST /api/videos/{video_id}/title-suggestions`
   - Users can create description suggestions: `POST /api/videos/{video_id}/description-suggestions`

3. **Vote on Suggestions**:
   - Vote on titles: `POST /api/title-suggestions/{suggestion_id}/vote`
   - Vote on descriptions: `POST /api/description-suggestions/{suggestion_id}/vote`
   - Each voter (identified by `voter_hash`) can only vote once per suggestion

4. **View Suggestions**:
   - Get all title suggestions for a video: `GET /api/videos/{video_id}/title-suggestions`
   - Get all description suggestions for a video: `GET /api/videos/{video_id}/description-suggestions`
   - Results are sorted by approval count (descending) and creation date

## Notes

- The `voter_hash` should be a unique identifier for each user (e.g., hash of IP address, user ID, or session ID)
- The approval count is automatically incremented when a vote is added
- Duplicate votes are prevented at the database level
- All endpoints return consistent `SuccessResponse` or `ErrorResponse` formats
- The project uses RQ (Redis Queue) for background job processing
- Rate limiting is implemented using FastAPILimiter with Redis

## Scheduled Tasks

- **Daily YouTube Video Fetch**: Automatically fetches videos from the YouTube channel once per day at 2:00 AM UTC
  - Configured in `app/main.py` using APScheduler
  - Runs in the background without user intervention
  - To change the schedule time, modify the CronTrigger in `app/main.py`

## Next Steps (Optional Enhancements)

1. Add authentication/authorization
2. Add pagination for large result sets
3. Add filtering and sorting options
4. Add endpoints to get top suggestions
5. Add webhook support for YouTube channel updates
6. Add caching for frequently accessed data
7. Add admin endpoint to manually trigger video fetch (with authentication)
