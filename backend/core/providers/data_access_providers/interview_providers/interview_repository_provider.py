from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from dependency_injector.wiring import Provide , inject
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.mongo import provide_interview_mongo_db
from backend.data_access.mongo.interview.interview_repository import InterviewRepository

# def get_interview_repository(
#     mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
# ) -> InterviewRepository:
#     return InterviewRepository(mongo_client)

@inject
def get_interview_repository (
    db: AsyncIOMotorDatabase = Depends(provide_interview_mongo_db),
    factory = Provide[RepositoriesContainer.interview_repository_factory]
)-> InterviewRepository:
    return factory(db)