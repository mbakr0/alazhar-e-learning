import redis
from rq import Queue
from app.core.config import REDIS_URL

redis_conn = redis.from_url(REDIS_URL,
    socket_timeout=5,
    health_check_interval=30)
video_queue = Queue("video_queue", connection=redis_conn)
suggestions_queue = Queue("suggestions_queue", connection=redis_conn)