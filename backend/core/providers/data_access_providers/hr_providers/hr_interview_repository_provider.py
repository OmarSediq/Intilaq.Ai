# app/core/providers/data_access_providers/hr_interview_repository_provider.py
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.providers.infra_providers import get_mongo_client
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository

def get_hr_interview_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> HRInterviewRepository:
    return HRInterviewRepository(mongo_client)
