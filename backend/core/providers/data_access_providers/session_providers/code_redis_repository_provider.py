from redis.asyncio import Redis
from backend.core.containers.infra_container import InfraContainer
from backend.core.containers.repositories_container import RepositoriesContainer 
from dependency_injector.wiring import Provide , inject 

from backend.data_access.redis.code_redis_repository import CodeRedisRepository

# async def get_code_redis_repository(
#     redis_client: Redis = Depends(get_redis_client),
# ) -> CodeRedisRepository:
#     return CodeRedisRepository(redis_client)
@inject 
def get_code_redis_repository (
    db : Redis = Provide[InfraContainer.redis_client],
    factory = Provide[RepositoriesContainer.code_redis_repository_factory]
)-> CodeRedisRepository:
    return factory(db)