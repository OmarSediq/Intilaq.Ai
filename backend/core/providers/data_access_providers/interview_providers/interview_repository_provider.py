from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.providers.infra_providers import get_mongo_client
from backend.data_access.mongo.interview.interview_repository import InterviewRepository

def get_interview_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> InterviewRepository:
    return InterviewRepository(mongo_client)
