from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.core.dependencies.session.mongo import provide_hr_interview_mongo_db
from backend.data_access.mongo.hr.hr_interview_evaluation_repository import HRInterviewEvaluationRepository
from dependency_injector.wiring import Provide , inject
from backend.core.containers.repositories_container import RepositoriesContainer

# def get_hr_interview_evaluation_repository(
#     client: AsyncIOMotorClient = Depends(get_mongo_client_raw),
# ) -> HRInterviewEvaluationRepository:
#     db = client["hr_db"]
#     return HRInterviewEvaluationRepository(db)
@inject 
def get_hr_interview_evaluation_repository (
    db : AsyncIOMotorDatabase = Depends(provide_hr_interview_mongo_db),
    factory = Provide[RepositoriesContainer.hr_interview_evaluation_repository_factory]
)-> HRInterviewEvaluationRepository:
    return factory(db)