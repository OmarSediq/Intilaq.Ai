from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.cv.education_repository import EducationRepository

# def get_education_repository(db: AsyncSession = Depends(get_db)) -> EducationRepository:
#     return EducationRepository(db)
@inject
def get_education_repository(
    db= Depends(provide_request_postgres_session), 
    factory = Provide[RepositoriesContainer.education_repository_factory]
)-> EducationRepository:
    return factory(db)

