from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.cv.resume_repository import ResumeRepository

# def get_resume_repository(db: AsyncSession = Depends(get_db)) -> ResumeRepository:
#     return ResumeRepository(db)

@inject 
def get_resume_repository (
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.resume_repository_factory]
)-> ResumeRepository:
    return factory(db)