from fastapi import Depends
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.data_access.postgres.cv.volunteering_repository import VolunteeringRepository

# def get_volunteering_repository(
#     db: AsyncSession = Depends(get_db)
# ) -> VolunteeringRepository:
#     return VolunteeringRepository(db)

@inject
def get_volunteering_repository(
    db = Depends(provide_request_postgres_session),
    factory = Provide[RepositoriesContainer.volunteering_repository_factory]
)-> VolunteeringRepository:
    return factory(db)