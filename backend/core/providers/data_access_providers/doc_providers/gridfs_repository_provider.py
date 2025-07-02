from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from backend.data_access.mongo.home.gridfs_storage_repository import GridFSStorageService
from backend.core.providers.infra_providers import get_mongo_client

def get_gridfs_storage(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
) -> GridFSStorageService:
    return GridFSStorageService(mongo_client)
