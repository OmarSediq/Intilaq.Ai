from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from backend.core.providers.infra_providers import get_mongo_client
from backend.data_access.mongo.home.interview_session_home_repository import InterviewSessionHomeRepository

def get_interview_home_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> InterviewSessionHomeRepository:
    return InterviewSessionHomeRepository(mongo_client)
