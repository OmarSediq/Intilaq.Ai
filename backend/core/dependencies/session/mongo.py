from dependency_injector.wiring import Provide, inject
from backend.core.containers.infra_container import InfraContainer
from motor.motor_asyncio import AsyncIOMotorDatabase , AsyncIOMotorGridFSBucket

@inject
def provide_interview_mongo_db(
    db: AsyncIOMotorDatabase = Provide[InfraContainer.mongo_db_factory.provided("interview_db")]
) -> AsyncIOMotorDatabase:
    return db

@inject
def provide_hr_interview_mongo_db(
    db: AsyncIOMotorDatabase = Provide[InfraContainer.mongo_db_factory.provided("hr_db")]
) -> AsyncIOMotorDatabase:
    return db

@inject 
def provide_resume_gridfs_bucket (
    db: AsyncIOMotorDatabase = Provide[InfraContainer.mongo_db_factory.provided("resumes_db")]
) -> AsyncIOMotorGridFSBucket:
    return AsyncIOMotorGridFSBucket(db)

@inject 
def provide_hr_video_bucket (
     db: AsyncIOMotorDatabase = Provide[InfraContainer.mongo_db_factory.provided("hr_db")]
) -> AsyncIOMotorGridFSBucket:
    return AsyncIOMotorGridFSBucket(db)
