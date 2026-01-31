# from fastapi import Depends
# from motor.motor_asyncio import AsyncIOMotorClient
# from backend.core.providers.infra_providers import get_mongo_client
# from backend.data_access.mongo.home.resume_download_repository import ResumeDownloadRepository

# def get_resume_download_repository(
#     mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
# ) -> ResumeDownloadRepository:
#     return ResumeDownloadRepository(mongo_client)
