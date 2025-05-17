from typing import Optional
from fastapi import HTTPException
from redis.asyncio import Redis

class CodeRedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def set_code(self, key: str, code: str, expire_seconds: int = 300):
        try:
            await self.redis.setex(key, expire_seconds, code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to set code in Redis: {e}")

    async def get_code(self, key: str) -> Optional[str]:
        try:
            return await self.redis.get(key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get code from Redisش: {e}")

    async def delete_code(self, key: str):
        try:
            return await self.redis.delete(key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete code from Redis: {e}")
