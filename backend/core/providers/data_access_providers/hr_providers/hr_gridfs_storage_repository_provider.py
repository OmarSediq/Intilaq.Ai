from motor.motor_asyncio import AsyncIOMotorClient
from backend.data_access.mongo.hr.hr_interview_gridfs_repository import HRGridFSStorageService
from backend.core.providers.infra_providers import get_mongo_client_raw

async def get_hr_gridfs_storage_service_async() -> HRGridFSStorageService:
    mongo_client: AsyncIOMotorClient =  await get_mongo_client_raw()
    db = mongo_client["hr_db"]
    return HRGridFSStorageService(db)
