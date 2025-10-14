# backend/providers/queue_provider.py
import os
from redis import Redis
from rq import Queue
from typing import Optional

_redis_conn: Optional[Redis] = None

def get_redis_conn() -> Redis:
    global _redis_conn
    if _redis_conn is None:
        redis_url = os.getenv("REDIS_URL", "redis://redis-container:6379")
        _redis_conn = Redis.from_url(redis_url ,socket_connect_timeout=5, socket_timeout=60)
    return _redis_conn

def get_queue(name: str = "default") -> Queue:
    conn = get_redis_conn()
    return Queue(name=name, connection=conn, default_timeout=int(os.getenv("RQ_DEFAULT_TIMEOUT", "1200")))
