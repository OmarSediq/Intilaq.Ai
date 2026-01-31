from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.cv.experience_repository import ExperienceRepository

# def get_experience_repository(db: AsyncSession = Depends(get_db)) -> ExperienceRepository:
#     return ExperienceRepository(db)
@inject
def get_experience_repository (
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.experience_repository_factory]
)-> ExperienceRepository: 
    return factory (db)