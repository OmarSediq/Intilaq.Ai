from fastapi import Depends
from backend.data_access.mongo.home.gridfs_storage_repository import GridFSStorageService
from backend.core.dependencies.session.mongo import provide_resume_gridfs_bucket
from motor.motor_asyncio import   AsyncIOMotorGridFSBucket
from dependency_injector.wiring import Provide , inject 
from backend.core.containers.repositories_container import RepositoriesContainer


@inject 
def get_gridfs_storage(
    bucket : AsyncIOMotorGridFSBucket = Depends(provide_resume_gridfs_bucket),
    factory = Provide[RepositoriesContainer.gridfs_storage_repository_factory]
)-> GridFSStorageService:
    return factory(bucket)

