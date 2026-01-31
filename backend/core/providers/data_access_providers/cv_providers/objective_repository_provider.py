from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.cv.objective_repository import CVObjectiveRepository

# def get_objective_repository(db: AsyncSession = Depends(get_db)) -> CVObjectiveRepository:
#     return CVObjectiveRepository(db)

@inject 
def get_objective_repository (
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.objective_repository_factory]
)-> CVObjectiveRepository:
    return factory(db)