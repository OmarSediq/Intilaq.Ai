from redis.asyncio import Redis
from backend.core.containers.infra_container import InfraContainer
from backend.core.containers.repositories_container import RepositoriesContainer 
from dependency_injector.wiring import Provide , inject 
from backend.data_access.redis.session_redis_repository import SessionRedisRepository

# async def get_session_redis_repository(
#     redis_client: Redis = Depends(get_redis_client),
# ) -> SessionRedisRepository:
#     return SessionRedisRepository(redis_client)

@inject 
def get_session_redis_repository (
    db : Redis = Provide[InfraContainer.redis_client],
    factory = Provide[RepositoriesContainer.session_redis_repository_factory]
)-> SessionRedisRepository : 
    return factory(db)