from typing import List

from psycopg2.extras import execute_values, RealDictCursor

from typing import Optional
from uuid import UUID
from datetime import datetime
from app.db.connection import db_pool
from app.domain.youtube import YouTubeVideo
from app.schemas.video_info import VideoInfo
from app.domain.models import (
    SuggestionVideo,
    titleSuggestions,
    descriptionSuggestions,
    lessonNameSuggestions,
    lecturerSuggestions,
    relatedSuggestion,
)


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
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM video_info")
            count = cur.fetchone()[0]
            return count
    finally:
        db_pool.putconn(conn)


def get_videos_for_catalog(related_only: bool = False):
    """List videos from video_info. If related_only=True, only videos users have marked as related (related votes > not_related)."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if related_only:
                cur.execute(
                    """
                    SELECT v.video_id, v.title, v.published_at, v.created_at
                    FROM video_info v
                    INNER JOIN (
                        SELECT video_id
                        FROM related_suggestions
                        GROUP BY video_id
                        HAVING COALESCE(SUM(CASE WHEN is_related THEN approval_count ELSE 0 END), 0)
                             > COALESCE(SUM(CASE WHEN NOT is_related THEN approval_count ELSE 0 END), 0)
                    ) r ON r.video_id = v.video_id
                    ORDER BY v.published_at DESC NULLS LAST
                    """
                )
            else:
                cur.execute(
                    """
                    SELECT video_id, title, published_at, created_at
                    FROM video_info
                    ORDER BY published_at DESC NULLS LAST
                    """
                )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        db_pool.putconn(conn)


# -------------------------------------------------------------------
# Title Suggestions Operations
# -------------------------------------------------------------------

def create_title_suggestion(video_id: str, title_text: str) -> titleSuggestions:
    """Create a new title suggestion."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO title_suggestions (video_id, title_text, approval_count)
                VALUES (%s, %s, 0)
                RETURNING id, video_id, title_text, approval_count, created_at
                """,
                (video_id, title_text)
            )
            row = cur.fetchone()
            conn.commit()
            return titleSuggestions(**row)
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


def get_title_suggestions_by_video(video_id: str, limit: int = 5) -> List[titleSuggestions]:
    """Get top N title suggestions for a video (default 5)."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, video_id, title_text, approval_count, created_at
                FROM title_suggestions
                WHERE video_id = %s
                ORDER BY approval_count DESC, created_at DESC
                LIMIT %s
                """,
                (video_id, limit)
            )
            rows = cur.fetchall()
            return [titleSuggestions(**row) for row in rows]
    finally:
        db_pool.putconn(conn)


def vote_title_suggestion(title_suggestion_id: UUID, voter_hash: str) -> bool:
    """Vote on a title suggestion. Returns True if vote was added, False if already voted."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            # Check if already voted
            cur.execute(
                """
                SELECT id FROM title_votes
                WHERE title_suggestion_id = %s AND voter_hash = %s
                """,
                (title_suggestion_id, voter_hash)
            )
            if cur.fetchone():
                return False
            
            # Add vote
            cur.execute(
                """
                INSERT INTO title_votes (title_suggestion_id, voter_hash)
                VALUES (%s, %s)
                """,
                (title_suggestion_id, voter_hash)
            )
            
            # Update approval count
            cur.execute(
                """
                UPDATE title_suggestions
                SET approval_count = approval_count + 1
                WHERE id = %s
                """,
                (title_suggestion_id,)
            )
            conn.commit()
            return True
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


# -------------------------------------------------------------------
# Description Suggestions Operations
# -------------------------------------------------------------------

def create_description_suggestion(video_id: str, description_text: str) -> descriptionSuggestions:
    """Create a new description suggestion."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO description_suggestions (video_id, description_text, approval_count)
                VALUES (%s, %s, 0)
                RETURNING id, video_id, description_text, approval_count, created_at
                """,
                (video_id, description_text)
            )
            row = cur.fetchone()
            conn.commit()
            return descriptionSuggestions(**row)
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


def get_description_suggestions_by_video(video_id: str, limit: int = 5) -> List[descriptionSuggestions]:
    """Get top N description suggestions for a video (default 5)."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, video_id, description_text, approval_count, created_at
                FROM description_suggestions
                WHERE video_id = %s
                ORDER BY approval_count DESC, created_at DESC
                LIMIT %s
                """,
                (video_id, limit)
            )
            rows = cur.fetchall()
            return [descriptionSuggestions(**row) for row in rows]
    finally:
        db_pool.putconn(conn)


def vote_description_suggestion(description_suggestion_id: UUID, voter_hash: str) -> bool:
    """Vote on a description suggestion. Returns True if vote was added, False if already voted."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            # Check if already voted
            cur.execute(
                """
                SELECT id FROM description_votes
                WHERE description_suggestion_id = %s AND voter_hash = %s
                """,
                (description_suggestion_id, voter_hash)
            )
            if cur.fetchone():
                return False
            
            # Add vote
            cur.execute(
                """
                INSERT INTO description_votes (description_suggestion_id, voter_hash)
                VALUES (%s, %s)
                """,
                (description_suggestion_id, voter_hash)
            )
            
            # Update approval count
            cur.execute(
                """
                UPDATE description_suggestions
                SET approval_count = approval_count + 1
                WHERE id = %s
                """,
                (description_suggestion_id,)
            )
            conn.commit()
            return True
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


# -------------------------------------------------------------------
# Lesson name suggestions
# -------------------------------------------------------------------

def create_lesson_name_suggestion(video_id: str, lesson_name_text: str) -> lessonNameSuggestions:
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO lesson_name_suggestions (video_id, lesson_name_text, approval_count)
                VALUES (%s, %s, 0)
                RETURNING id, video_id, lesson_name_text, approval_count, created_at
                """,
                (video_id, lesson_name_text)
            )
            row = cur.fetchone()
            conn.commit()
            return lessonNameSuggestions(**row)
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


def get_lesson_name_suggestions_by_video(video_id: str, limit: int = 5) -> List[lessonNameSuggestions]:
    """Get top N lesson name suggestions for a video (default 5)."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, video_id, lesson_name_text, approval_count, created_at
                FROM lesson_name_suggestions WHERE video_id = %s
                ORDER BY approval_count DESC, created_at DESC
                LIMIT %s
                """,
                (video_id, limit)
            )
            return [lessonNameSuggestions(**r) for r in cur.fetchall()]
    finally:
        db_pool.putconn(conn)


def vote_lesson_name_suggestion(suggestion_id: UUID, voter_hash: str) -> bool:
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM lesson_name_votes WHERE lesson_name_suggestion_id = %s AND voter_hash = %s",
                (suggestion_id, voter_hash)
            )
            if cur.fetchone():
                return False
            cur.execute(
                "INSERT INTO lesson_name_votes (lesson_name_suggestion_id, voter_hash) VALUES (%s, %s)",
                (suggestion_id, voter_hash)
            )
            cur.execute(
                "UPDATE lesson_name_suggestions SET approval_count = approval_count + 1 WHERE id = %s",
                (suggestion_id,)
            )
            conn.commit()
            return True
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


# -------------------------------------------------------------------
# Lecturer name suggestions
# -------------------------------------------------------------------

def create_lecturer_suggestion(video_id: str, lecturer_name_text: str) -> lecturerSuggestions:
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO lecturer_suggestions (video_id, lecturer_name_text, approval_count)
                VALUES (%s, %s, 0)
                RETURNING id, video_id, lecturer_name_text, approval_count, created_at
                """,
                (video_id, lecturer_name_text)
            )
            row = cur.fetchone()
            conn.commit()
            return lecturerSuggestions(**row)
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


def get_lecturer_suggestions_by_video(video_id: str, limit: int = 5) -> List[lecturerSuggestions]:
    """Get top N lecturer suggestions for a video (default 5)."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, video_id, lecturer_name_text, approval_count, created_at
                FROM lecturer_suggestions WHERE video_id = %s
                ORDER BY approval_count DESC, created_at DESC
                LIMIT %s
                """,
                (video_id, limit)
            )
            return [lecturerSuggestions(**r) for r in cur.fetchall()]
    finally:
        db_pool.putconn(conn)


def vote_lecturer_suggestion(suggestion_id: UUID, voter_hash: str) -> bool:
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM lecturer_votes WHERE lecturer_suggestion_id = %s AND voter_hash = %s",
                (suggestion_id, voter_hash)
            )
            if cur.fetchone():
                return False
            cur.execute(
                "INSERT INTO lecturer_votes (lecturer_suggestion_id, voter_hash) VALUES (%s, %s)",
                (suggestion_id, voter_hash)
            )
            cur.execute(
                "UPDATE lecturer_suggestions SET approval_count = approval_count + 1 WHERE id = %s",
                (suggestion_id,)
            )
            conn.commit()
            return True
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


# -------------------------------------------------------------------
# Related (is_related): users vote whether the video is related or not
# -------------------------------------------------------------------

def get_related_suggestions_by_video(video_id: str) -> List[relatedSuggestion]:
    """Get the two options (related / not_related) and their vote counts for a video."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, video_id, is_related, approval_count, created_at
                FROM related_suggestions
                WHERE video_id = %s
                ORDER BY is_related DESC
                """,
                (video_id,)
            )
            return [relatedSuggestion(**r) for r in cur.fetchall()]
    finally:
        db_pool.putconn(conn)


def get_or_create_related_suggestion(video_id: str, is_related: bool) -> relatedSuggestion:
    """Get or create the (video_id, is_related) row and return it."""
    conn = db_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO related_suggestions (video_id, is_related, approval_count)
                VALUES (%s, %s, 0)
                ON CONFLICT (video_id, is_related) DO NOTHING
                """,
                (video_id, is_related)
            )
            cur.execute(
                """
                SELECT id, video_id, is_related, approval_count, created_at
                FROM related_suggestions WHERE video_id = %s AND is_related = %s
                """,
                (video_id, is_related)
            )
            row = cur.fetchone()
            conn.commit()
            return relatedSuggestion(**row)
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)


def vote_related_suggestion(suggestion_id: UUID, voter_hash: str) -> bool:
    """Vote on a related/not_related option. Returns True if vote was added."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM related_votes WHERE related_suggestion_id = %s AND voter_hash = %s",
                (suggestion_id, voter_hash)
            )
            if cur.fetchone():
                return False
            cur.execute(
                "INSERT INTO related_votes (related_suggestion_id, voter_hash) VALUES (%s, %s)",
                (suggestion_id, voter_hash)
            )
            cur.execute(
                "UPDATE related_suggestions SET approval_count = approval_count + 1 WHERE id = %s",
                (suggestion_id,)
            )
            conn.commit()
            return True
    except Exception:
        conn.rollback()
        raise
    finally:
        db_pool.putconn(conn)
