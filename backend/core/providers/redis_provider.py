# backend/core/providers/redis_provider.py
import os
import logging
import asyncio
import time
from typing import Any, Dict, Optional

import redis.asyncio as redis  # redis-py asyncio API

logger = logging.getLogger("backend.core.providers.redis_provider")

# --- Config from env (explicit full names) ---
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_DECODE_RESPONSES: bool = os.getenv("REDIS_DECODE_RESPONSES", "true").lower() == "true"
REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
REDIS_SOCKET_TIMEOUT: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))

# Idempotency / claim defaults
IDEMPOTENCY_CLAIM_TTL_SECONDS: int = int(os.getenv("IDEMPOTENCY_CLAIM_TTL_SECONDS", "60"))

# Internal singleton
_redis_client: Optional[redis.Redis] = None
_redis_lock = asyncio.Lock()


async def get_redis_client() -> redis.Redis:
    """
    Return a singleton redis.asyncio.Redis client.
    Use await get_redis_client() wherever you need a connection.
    This function ensures only one instance is created (per process).
    """
    global _redis_client
    if _redis_client is None:
        async with _redis_lock:
            if _redis_client is None:
                # create client with connection pool tuning
                _redis_client = redis.from_url(
                    REDIS_URL,
                    decode_responses=REDIS_DECODE_RESPONSES,
                    socket_timeout=REDIS_SOCKET_TIMEOUT,
                    max_connections=REDIS_MAX_CONNECTIONS,
                )
                # optional: test ping with backoff
                await _ensure_redis_ready(_redis_client)
    return _redis_client


async def _ensure_redis_ready(client: redis.Redis, retries: int = 3, delay: float = 0.5):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            # ping is coroutine in redis.asyncio
            await client.ping()
            logger.info("Redis connection established to %s", REDIS_URL)
            return
        except Exception as exc:
            last_exc = exc
            logger.warning("Redis ping failed (attempt %s/%s): %s", attempt, retries, exc)
            await asyncio.sleep(delay * attempt)
    logger.error("Redis not reachable after %s attempts: %s", retries, last_exc)
    raise RuntimeError("Redis connection failed") from last_exc


# --- Helpers: Streams & Idempotency claim ---

async def stream_xadd(stream_name: str, payload: Dict[str, Any], *, max_len: Optional[int] = None, approximate: bool = True) -> str:
    """
    Add a message to a Redis stream. Payload values are coerced to str.
    Returns the message id.
    """
    client = await get_redis_client()
    # convert payload values to strings (redis expects mapping of str->str)
    mapping = {str(k): (v if isinstance(v, str) else str(v)) for k, v in payload.items()}
    if max_len:
        return await client.xadd(stream_name, mapping, maxlen=max_len, approximate=approximate)
    return await client.xadd(stream_name, mapping)


async def stream_xlen(stream_name: str) -> int:
    client = await get_redis_client()
    return await client.xlen(stream_name)


async def stream_xreadgroup(group: str, consumer: str, streams: Dict[str, str], *, count: int = 1, block: int = 1000):
    """
    Wrapper around xreadgroup. `streams` is mapping {stream_name: id} e.g. { "mystream": ">" }.
    """
    client = await get_redis_client()
    return await client.xreadgroup(group, consumer, streams, count=count, block=block)


async def stream_xack(stream_name: str, group: str, message_id: str):
    client = await get_redis_client()
    return await client.xack(stream_name, group, message_id)


async def stream_xpending(stream_name: str, group: str, start: str = "-", end: str = "+", count: int = 10):
    client = await get_redis_client()
    return await client.xpending(stream_name, group, start, end, count)


# Short-lived claim helper (SET key value NX EX)
async def claim_short(claim_key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
    client = await get_redis_client()
    ttl = ttl_seconds if ttl_seconds is not None else IDEMPOTENCY_CLAIM_TTL_SECONDS
    return await client.set(claim_key, value, nx=True, ex=ttl)


async def release_claim(claim_key: str):
    client = await get_redis_client()
    try:
        await client.delete(claim_key)
    except Exception:
        logger.exception("release_claim failed for %s", claim_key)


# Health check helper used by orchestration / readiness probes
async def redis_healthcheck() -> Dict[str, Any]:
    client = await get_redis_client()
    info = await client.info()
    # return small payload used by readiness check or metrics
    return {
        "connected_clients": info.get("connected_clients"),
        "used_memory_human": info.get("used_memory_human"),
        "role": info.get("role"),
        "uptime_in_seconds": info.get("uptime_in_seconds"),
    }


# Close client (used in shutdown hooks)
async def close_redis_client():
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.close()
            await _redis_client.connection_pool.disconnect()
        except Exception:
            logger.exception("failed to close redis client")
        _redis_client = None
