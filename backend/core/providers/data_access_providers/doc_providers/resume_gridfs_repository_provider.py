# from fastapi import Depends
# from dependency_injector.wiring import Provide , inject 
# from backend.core.containers.repositories_container import RepositoriesContainer
# from backend.data_access.mongo.home.resume_gridfs_repository import ResumeGridFSRepository
# from backend.core.dependencies.session.mongo import provide_resume_gridfs_bucket
# from motor.motor_asyncio import   AsyncIOMotorGridFSBucket


# @inject
# def get_resume_gridfs_repository (
#     bucket : AsyncIOMotorGridFSBucket = Depends(provide_resume_gridfs_bucket),
#     factory = Provide[RepositoriesContainer.resume_gridfs_repository_factory]
# )-> ResumeGridFSRepository:
#     return factory(bucket)

