from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.hr.hr_auth_repository import HRRepository

# def get_hr_repository(db: AsyncSession = Depends(get_db)) -> HRRepository:
#     return HRRepository(db)

@inject 
def get_hr_repository (
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.hr_auth_repository_factory]
)-> HRRepository:
    return factory(db)