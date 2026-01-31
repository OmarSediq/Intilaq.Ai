from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.cv.certification_repository import CertificationRepository

# def get_certification_repository(db: AsyncSession = Depends(get_db)) -> CertificationRepository:
#     return CertificationRepository(db)


@inject 
def get_certification_repository (
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.certification_repository_factory]
) -> CertificationRepository:
    return factory(db)