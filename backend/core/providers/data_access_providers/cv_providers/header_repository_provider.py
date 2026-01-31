from fastapi import Depends
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from dependency_injector.wiring import Provide , inject
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session



# def get_header_repository(db: AsyncSession = Depends(get_db)) -> CVHeaderRepository:
#     return CVHeaderRepository(db)


@inject 
def get_header_repository (
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.header_repository_factory]
) -> CVHeaderRepository:
    return factory(db)


