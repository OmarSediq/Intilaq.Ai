from fastapi import Depends
from backend.data_access.mongo.hr.hr_interview_gridfs_repository import HRGridFSStorageService
from motor.motor_asyncio import   AsyncIOMotorGridFSBucket
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.mongo import provide_hr_video_bucket


# def get_hr_gridfs_storage_service_async() -> HRGridFSStorageService:
#     mongo_client: AsyncIOMotorClient =   get_mongo_client_raw()
#     db = mongo_client["hr_db"]
#     return HRGridFSStorageService(db)


@inject 
def get_hr_gridfs_storage_service_async(
    bucket : AsyncIOMotorGridFSBucket = Depends(provide_hr_video_bucket),
    factory = Provide[RepositoriesContainer.hr_gridfs_storage_repository_factory]
)-> HRGridFSStorageService:
    return factory(bucket)

