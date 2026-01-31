from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.hr.hr_user_repository import HRUserRepository

# async def get_hr_user_repository(db: AsyncSession = Depends(get_db)) -> HRUserRepository:
#     return HRUserRepository(db)

@inject 
def get_hr_user_repository (
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.hr_user_repository_factory]
)->HRUserRepository:
    return factory(db)