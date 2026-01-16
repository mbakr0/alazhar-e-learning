from typing import List

from psycopg2.extras import execute_values, RealDictCursor

from app.db.connection import db_pool
from app.domain.youtube import YouTubeVideo
from app.schemas.video_info import VideoInfo
from app.domain.models import SuggestionVideo


# -------------------------------------------------------------------
# Query helpers
# -------------------------------------------------------------------

def row_to_suggestion(row: dict) -> SuggestionVideo:
    """
    Convert a DB row dict into a SuggestionVideo domain model.
    """
    return SuggestionVideo(**row)


# -------------------------------------------------------------------
# Read operations
# -------------------------------------------------------------------
def get_all_suggest_videos():
    """Fetch all videos from the database."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    *
                FROM suggestion_video_info 
                WHERE is_related_video = TRUE
                """
            )
            rows = cur.fetchall()
            return [row_to_suggestion(row) for row in rows]
    finally:
        db_pool.putconn(conn)


def get_suggest_videos(ids: List[str]) -> List[SuggestionVideo]:
    """
    Fetch suggestion videos by video_id.
    """
    if not ids:
        return []

    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    video_id,
                    main_level,
                    common_sub_level,
                    specialized_level,
                    lecture_title,
                    lesson_name,
                    batch,
                    is_related_video
                FROM suggestion_video_info
                WHERE video_id = ANY(%s)
                AND is_related_video = TRUE
                """,
                (ids,),
            )
            rows = cur.fetchall()
            return [row_to_suggestion(row) for row in rows]
    finally:
        db_pool.putconn(conn)


# -------------------------------------------------------------------
# Write operations
# -------------------------------------------------------------------

def insert_suggestion_videos(videos: List[VideoInfo]) -> None:
    """
    Insert suggested video metadata.
    """
    if not videos:
        return

    values = [
        (
            v.video_id,
            v.main_level,
            v.common_sub_level,
            v.specialized_level,
            v.lecture_title,
            v.lesson_name,
            v.batch,
            v.is_related_video
        )
        for v in videos
    ]

    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO suggestion_video_info (
                    video_id,
                    main_level,
                    common_sub_level,
                    specialized_level,
                    lecture_title,
                    lesson_name,
                    batch,
                    is_related_video
                )
                VALUES %s
                ON CONFLICT (video_id) DO NOTHING
                """,
                values,
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


def insert_youtube_videos(videos: List[YouTubeVideo]) -> None:
    """
    Insert YouTube video base metadata.
    """
    if not videos:
        return

    values = [
        (
            v.video_id,
            v.title,
            v.published_at,
        )
        for v in videos
    ]

    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO video_info (
                    video_id,
                    title,
                    published_at
                )
                VALUES %s
                ON CONFLICT (video_id) DO NOTHING
                """,
                values,
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


def get_videos_count() -> int:
    conn = db_pool.getconn()
    try:
        with conn.curser() as cur:
            cur.execute("SELECT COUNT(*) FROM video_info")
            count = cur.fetchone()[0]
            return count
    finally:
        db_pool.putconn(conn)
