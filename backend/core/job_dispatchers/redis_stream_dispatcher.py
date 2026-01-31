
import json
import logging
import asyncio
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class RedisStreamDispatcher:
    def __init__(self, redis_client, stream_name: str, group: Optional[str] = None):
        """
        redis_client: instance of redis.asyncio.Redis
        stream_name: name of the stream, e.g. "render_tasks"
        group: optional consumer-group name (اختياري)
        """
        self.redis = redis_client
        self.stream_name = stream_name
        self.group = group or f"group-{stream_name}"

    # -----------------------
    # Internal helpers
    # -----------------------
    def _normalize_value(self, v: Any) -> str:
        """Normalize a python value into a string suitable for Redis stream fields."""
        if v is None:
            return ""
        if isinstance(v, str):
            return v
        # for dict/list use json dumps (compact)
        if isinstance(v, (dict, list)):
            try:
                return json.dumps(v, separators=(",", ":"), default=str)
            except Exception:
                return json.dumps(str(v))
        # for primitives (int/float/bool) -> str
        return str(v)

    # -----------------------
    # Public API
    # -----------------------
    async def enqueue(self, fields: Dict[str, Any], maxlen: int = 1000, approximate: bool = True) -> str:
        """
        Add an entry to Redis stream.
        - fields: flat dict of key -> value (any JSON-serializable).
          Prefer the domain to include keys like: task_id, job_id, html_gridfs_id, type, payload (small).
        - returns: Redis XADD message id (str).
        """
        if not isinstance(fields, dict):
            raise TypeError("fields must be a dict[str, Any]")

        # normalize to str values
        normalized = {k: self._normalize_value(v) for k, v in fields.items()}

        try:
            if approximate:
                msg_id = await self.redis.xadd(self.stream_name, normalized, maxlen=maxlen, approximate=True)
            else:
                msg_id = await self.redis.xadd(self.stream_name, normalized, maxlen=maxlen)
            logger.debug("Enqueued to stream %s id=%s keys=%s", self.stream_name, msg_id, list(fields.keys()))
            return msg_id
        except Exception as exc:
            logger.exception("RedisStreamDispatcher.enqueue failed")
            raise

    # -----------------------
    # Ops helpers
    # -----------------------
    async def ensure_group(self, start_id: str = "$", mkstream: bool = True) -> None:
        """
        Ensure consumer group exists. Safe to call at startup.
        - start_id: initial id for group (default '$' to read new messages)
        - mkstream: if True create stream if missing
        """
        try:
            # XGROUP CREATE <stream> <group> <id> MKSTREAM
            await self.redis.xgroup_create(self.stream_name, self.group, id=start_id, mkstream=mkstream)
            logger.info("Created consumer group %s on stream %s", self.group, self.stream_name)
        except Exception as e:
            # ignore BUSYGROUP (group exists)
            if "BUSYGROUP" in str(e) or "busy group" in str(e).lower():
                logger.debug("Consumer group %s already exists", self.group)
            else:
                logger.exception("Failed to create redis consumer group")
                raise