# Alazhar E-Learning Platform

A FastAPI-based application that integrates with YouTube to automatically fetch videos from a specific channel, store them in a Supabase (PostgreSQL) database, and allows users to suggest and vote on improved video titles and descriptions.

## Features

- 🔄 **Automatic Video Fetching**: Daily scheduled task fetches latest videos from YouTube channel
- 💡 **User Suggestions**: Users can suggest better titles and descriptions for videos
- 👍 **Voting System**: Users can vote on suggestions with approval counting
- 📊 **Video Management**: Track and manage video metadata with academic level categorization
- ⚡ **Fast API**: Built with FastAPI for high performance
- 🔒 **Rate Limiting**: Built-in rate limiting to prevent abuse
- 🗄️ **PostgreSQL**: Uses Supabase (PostgreSQL) for data storage
- 🔄 **Background Jobs**: Redis Queue (RQ) for asynchronous video processing

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **Cache/Queue**: Redis
- **Task Queue**: RQ (Redis Queue)
- **Scheduler**: APScheduler
- **API Client**: Google YouTube Data API v3

## Prerequisites

- Python 3.12+
- PostgreSQL database (Supabase)
- Redis server
- YouTube Data API v3 key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alazhar-e-learning
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv alazhar-env
   
   # On Windows
   alazhar-env\Scripts\activate
   
   # On Linux/Mac
   source alazhar-env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.text
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   USER=your_db_user
   PASSWORD=your_db_password
   HOST=your_db_host
   PORT=5432
   DATABASE_Name=your_database_name
   YOUTUBE_API_KEY=your_youtube_api_key
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Set up the database**
   
   Run the SQL schema file in your Supabase SQL editor:
   ```bash
   # Copy the contents of database_schema.sql and run it in Supabase
   ```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Start RQ Worker

In a separate terminal, start the Redis Queue worker:

```bash
rq worker video_queue
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Video Endpoints

#### Get All Videos
```
GET /api/videos
```
Returns all videos that are marked as related videos.

**Response:**
```json
{
  "success": true,
  "message": "Videos fetched successfully",
  "data": [
    {
      "video_id": "abc123",
      "main_level": "التمهيدية",
      "common_sub_level": "المستوى الأول",
      "lecture_title": "Introduction",
      ...
    }
  ]
}
```

#### Add Videos
```
POST /api/videos
```
Adds videos to the queue for processing.

**Request Body:**
```json
[
  {
    "video_id": "abc123",
    "main_level": "التمهيدية",
    "is_related_video": true
  }
]
```

### Suggestion Endpoints

#### Create Title Suggestion
```
POST /api/videos/{video_id}/title-suggestions
```
Creates a new title suggestion for a video.

**Request Body:**
```json
{
  "video_id": "abc123",
  "title_text": "Improved Title"
}
```

#### Get Title Suggestions
```
GET /api/videos/{video_id}/title-suggestions
```
Returns all title suggestions for a video, sorted by approval count.

#### Create Description Suggestion
```
POST /api/videos/{video_id}/description-suggestions
```
Creates a new description suggestion for a video.

**Request Body:**
```json
{
  "video_id": "abc123",
  "description_text": "Improved description"
}
```

#### Get Description Suggestions
```
GET /api/videos/{video_id}/description-suggestions
```
Returns all description suggestions for a video, sorted by approval count.

### Voting Endpoints

#### Vote on Title Suggestion
```
POST /api/title-suggestions/{suggestion_id}/vote
```
Votes on a title suggestion. Each user (identified by `voter_hash`) can only vote once.

**Request Body:**
```json
{
  "voter_hash": "user_unique_hash"
}
```

#### Vote on Description Suggestion
```
POST /api/description-suggestions/{suggestion_id}/vote
```
Votes on a description suggestion. Each user (identified by `voter_hash`) can only vote once.

**Request Body:**
```json
{
  "voter_hash": "user_unique_hash"
}
```

### YouTube Endpoints

#### Get Video Count
```
GET /api/youtube/count
```
Returns the total number of videos on the YouTube channel.

**Response:**
```json
{
  "success": true,
  "message": "Video count fetched successfully",
  "data": {
    "count": 150
  }
}
```

## Scheduled Tasks

The application automatically fetches videos from the YouTube channel **once per day at 2:00 AM UTC**. This is handled by APScheduler running in the background.

To change the schedule time, modify the `CronTrigger` in `app/main.py`:

```python
scheduler.add_job(
    fetch_and_store_youtube_videos,
    trigger=CronTrigger(hour=2, minute=0),  # Change time here
    ...
)
```

## Database Schema

The application uses the following main tables:

- `video_info` - Base YouTube video data
- `suggestion_video_info` - Extended metadata for videos
- `title_suggestions` - User suggestions for video titles
- `description_suggestions` - User suggestions for video descriptions
- `title_votes` - Votes on title suggestions
- `description_votes` - Votes on description suggestions
- `video_votes` - Votes on videos

See `database_schema.sql` for the complete schema.

## Rate Limiting

All endpoints are protected with rate limiting:

- Video operations: 10 requests/minute
- Suggestion creation: 20 requests/minute
- Suggestion fetching: 30 requests/minute
- Voting: 50 requests/minute
- YouTube count: 10 requests/minute

## Configuration

### YouTube Channel Configuration

Edit `app/core/config.py` to change the YouTube channel:

```python
PLAYLIST_ID = "UUUoYtTky7mURqrkp593xAgw"
CHANNEL_ID = "UCUoYtTky7mURqrkp593xAgw"
```

## Project Structure

```
alazhar-e-learning/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── videos.py          # Video endpoints
│   │       ├── suggestions.py     # Suggestion endpoints
│   │       └── youtube.py         # YouTube endpoints
│   ├── core/
│   │   └── config.py              # Configuration
│   ├── db/
│   │   ├── connection.py          # Database connection
│   │   └── repo/
│   │       └── videos_repo.py     # Database operations
│   ├── domain/
│   │   ├── models.py              # Domain models
│   │   ├── enum.py                # Enumerations
│   │   └── youtube.py             # YouTube domain models
│   ├── mappers/
│   │   ├── video_mapper.py        # Data mappers
│   │   └── youtube_mapper.py      # YouTube mappers
│   ├── queues/
│   │   └── redis_queue.py         # Redis queue setup
│   ├── schemas/
│   │   ├── video_info.py          # Pydantic schemas
│   │   ├── suggestions.py         # Suggestion schemas
│   │   └── responses.py           # Response schemas
│   ├── services/
│   │   ├── youtube_service.py     # YouTube API service
│   │   └── suggestion_service.py # Suggestion service
│   ├── workers/
│   │   ├── video_worker.py       # Video processing worker
│   │   └── youtube_scheduler.py   # Scheduled YouTube fetch
│   └── main.py                    # FastAPI application
├── database_schema.sql            # Database schema
├── requirements.text              # Python dependencies
├── PROJECT_SUMMARY.md             # Detailed project summary
└── README.md                      # This file
```

## Development

### Running Tests

```bash
# Add tests when available
pytest
```

### Code Style

The project follows PEP 8 Python style guidelines.

## Deployment

### Using Render

The project includes a `render.yaml` configuration file for deployment on Render.com.

1. Push your code to GitHub
2. Connect your repository to Render
3. Render will automatically detect the `render.yaml` file
4. Set environment variables in Render dashboard

### Environment Variables for Production

Make sure to set all required environment variables in your hosting platform:
- `USER`
- `PASSWORD`
- `HOST`
- `PORT`
- `DATABASE_Name`
- `YOUTUBE_API_KEY`
- `REDIS_URL`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Add your license here]

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- FastAPI for the excellent web framework
- Supabase for the PostgreSQL database
- Google YouTube Data API for video data
