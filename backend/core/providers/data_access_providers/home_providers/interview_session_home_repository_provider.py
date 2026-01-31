from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from dependency_injector.wiring import Provide , inject
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.mongo import provide_interview_mongo_db
from backend.data_access.mongo.home.interview_session_home_repository import InterviewSessionHomeRepository

# def get_interview_home_repository(
#     mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
# ) -> InterviewSessionHomeRepository:
#     return InterviewSessionHomeRepository(mongo_client)

@inject 
def get_interview_home_repository (
    db : AsyncIOMotorDatabase = Depends(provide_interview_mongo_db),
    factory = Provide[RepositoriesContainer.interview_session_home_repository_factory]
)-> InterviewSessionHomeRepository: 
    return factory(db)
