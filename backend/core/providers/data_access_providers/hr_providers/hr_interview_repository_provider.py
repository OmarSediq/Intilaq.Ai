from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.core.providers.infra_providers import get_mongo_client
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository

def get_hr_interview_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> HRInterviewRepository:
    db: AsyncIOMotorDatabase = mongo_client["hr_db"]
    return HRInterviewRepository(db)