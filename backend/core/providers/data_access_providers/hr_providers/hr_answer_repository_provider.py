from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.core.providers.infra_providers import get_mongo_client

def get_hr_answer_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
) -> HRAnswerRepository:
    db = mongo_client["hr_db"]
    return HRAnswerRepository(db=db)
