from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.user_repository import UserRepository

# def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
#     return UserRepository(db)


@inject 
def get_user_repository (
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.user_repository_factory.provider]

)->UserRepository:
   return factory (db)