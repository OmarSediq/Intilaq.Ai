import redis.asyncio as redis
from Core.config import settings

async def get_redis():
    client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )
    await client.ping()
    return client
