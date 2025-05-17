from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.providers.infra_providers import get_mongo_client
from backend.data_access.mongo.home.resume_gridfs_repository import ResumeGridFSRepository

def get_resume_gridfs_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> ResumeGridFSRepository:
    return ResumeGridFSRepository(mongo_client)
