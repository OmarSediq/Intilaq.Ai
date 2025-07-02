from redis.asyncio import Redis
from fastapi import Depends
from backend.core.providers.infra_providers import get_redis_client
from backend.data_access.redis.code_redis_repository import CodeRedisRepository

async def get_code_redis_repository(
    redis_client: Redis = Depends(get_redis_client),
) -> CodeRedisRepository:
    return CodeRedisRepository(redis_client)
