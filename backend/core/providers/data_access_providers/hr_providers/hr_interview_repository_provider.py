from fastapi import Depends
from motor.motor_asyncio import  AsyncIOMotorDatabase
from backend.core.dependencies.session.mongo import provide_hr_interview_mongo_db
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from dependency_injector.wiring import Provide , inject
from backend.core.containers.repositories_container import RepositoriesContainer
# def get_hr_interview_repository(
#     mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
# ) -> HRInterviewRepository:
#     db: AsyncIOMotorDatabase = mongo_client["hr_db"]
#     return HRInterviewRepository(db)

@inject 
def get_hr_interview_repository (
    db : AsyncIOMotorDatabase = Depends(provide_hr_interview_mongo_db),
    factory = Provide[RepositoriesContainer.hr_interview_repository_factory]
)-> HRInterviewRepository: 
    return factory(db)