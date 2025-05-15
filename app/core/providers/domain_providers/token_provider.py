from redis.asyncio import Redis
from fastapi import Depends
from app.core.providers.infra_providers import get_redis_client
from app.domain_services.token_services.token_service import TokenService

def get_token_service(redis_client: Redis = Depends(get_redis_client)) -> TokenService:
    return TokenService(redis_client)
