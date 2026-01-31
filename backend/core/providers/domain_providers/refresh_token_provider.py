from dependency_injector.wiring import Provide, inject
from backend.core.containers.infra_container import InfraContainer
from redis.asyncio import Redis
from backend.domain_services.token_services.refresh_token_service import RefreshTokenService

@inject
def get_refresh_token_service(
    redis_client: Redis = Provide[InfraContainer.redis_client],
) -> RefreshTokenService:
    return RefreshTokenService(redis_client)
