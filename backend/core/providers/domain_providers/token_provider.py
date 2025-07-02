from redis.asyncio import Redis
from backend.core.providers.infra_providers import get_redis_client
from backend.domain_services.token_services.token_service import TokenService


async def get_token_service() -> TokenService:
    redis_client: Redis = await get_redis_client()  
    return TokenService(redis_client)
