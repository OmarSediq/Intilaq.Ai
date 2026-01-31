from motor.motor_asyncio import  AsyncIOMotorDatabase
from fastapi import Depends
from dependency_injector.wiring import Provide , inject
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.mongo import provide_hr_interview_mongo_db
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository


# def get_hr_answer_repository() -> HRAnswerRepository:
#     client: AsyncIOMotorClient = get_mongo_client_raw()
#     db = client["hr_db"]
#     return HRAnswerRepository(db=db)

@inject
def get_hr_answer_repository (
    db : AsyncIOMotorDatabase = Depends(provide_hr_interview_mongo_db),
    factory = Provide[RepositoriesContainer.hr_interview_client_repository_factory]
)-> HRAnswerRepository : 
    return factory(db)