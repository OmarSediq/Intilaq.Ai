from redis.asyncio import Redis
from fastapi import Depends
from backend.core.providers.infra_providers import get_redis_client
from backend.data_access.redis.session_redis_repository import SessionRedisRepository

async def get_session_redis_repository(
    redis_client: Redis = Depends(get_redis_client),
) -> SessionRedisRepository:
    return SessionRedisRepository(redis_client)
