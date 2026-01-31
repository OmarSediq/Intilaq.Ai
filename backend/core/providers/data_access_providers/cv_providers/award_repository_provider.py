from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.cv.award_repository import AwardRepository

# def get_award_repository(db: AsyncSession = Depends(get_db)) -> AwardRepository:
#     return AwardRepository(db)

@inject
def get_award_repository (
    db = Depends(provide_request_postgres_session) , 
    factory = Provide[RepositoriesContainer.award_repository_factory]
)-> AwardRepository:
    return factory(db)
