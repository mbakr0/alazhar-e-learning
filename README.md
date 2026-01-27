# Alazhar E-Learning

FastAPI app that syncs videos from a YouTube channel (daily) into Supabase and lets users **suggest** and **vote** on titles, descriptions, lesson names, and lecturer names. All writes go through a Redis queue; reads hit the DB.

**Stack:** FastAPI, PostgreSQL (Supabase), Redis, RQ, APScheduler.

## Setup

- Python 3.12+, Redis, Supabase (PostgreSQL), YouTube Data API key.

```bash
python -m venv alazhar-env
# Windows: alazhar-env\Scripts\activate
# Linux/Mac: source alazhar-env/bin/activate
pip install -r requirements.text
```

Create `.env`:

```env
USER=...
PASSWORD=...
HOST=...
PORT=5432
DATABASE_Name=...
YOUTUBE_API_KEY=...
REDIS_URL=redis://localhost:6379/0
```

Run `database_schema.sql` in the Supabase SQL editor.

## Run

```bash
uvicorn app.main:app --reload
```

The app starts an RQ worker for `video_queue` and `suggestions_queue`. API: `http://localhost:8000`. Docs: `/docs`, `/redoc`.

## API (short)

- **GET /api/videos** — List videos. Use `?related_only=true` to return only videos users have marked as related.
- **GET /api/youtube/count** — Channel video count.

**Flow:** For each video, the app shows the **top 5** suggestions per type (title, description, lesson name, lecturer). The user either **votes on one of them** or **submits their own**. For **is_related**, users vote whether the video is related or not; the catalog can be filtered to only related videos.

Suggestions: GET returns top 5 by default (`?limit=5`); create/vote are queued (202 + `job_id`).

| Type   | GET (top 5)                             | Vote on existing                  | Submit your own (POST)                |
|--------|----------------------------------------|-----------------------------------|---------------------------------------|
| Title  | `GET /api/videos/{id}/title-suggestions` | `POST /api/title-suggestions/{id}/vote` | `POST /api/videos/{id}/title-suggestions` |
| Description | same pattern                        | …/description-suggestions/{id}/vote | …/description-suggestions             |
| Lesson name | same pattern                      | …/lesson-name-suggestions/{id}/vote | …/lesson-name-suggestions             |
| Lecturer | same pattern                        | …/lecturer-suggestions/{id}/vote   | …/lecturer-suggestions                |
| **Is related** | `GET /api/videos/{id}/related-suggestions` (returns related / not_related + counts) | — | `POST /api/videos/{id}/related-vote` body `{"is_related": true/false, "voter_hash":"..."}` |

Vote body: `{"voter_hash":"..."}`. Create bodies: `{"video_id":"...", "title_text":"..."}` (or `description_text`, `lesson_name_text`, `lecturer_name_text`).

## Other

- **Daily sync:** YouTube videos are fetched once per day (e.g. 02:00 UTC). See `app/main.py` to change the schedule.
- **Channel:** Set `PLAYLIST_ID` and `CHANNEL_ID` in `app/core/config.py`.
- More detail: `PROJECT_SUMMARY.md`, `database_schema.sql`.
