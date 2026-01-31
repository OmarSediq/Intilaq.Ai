from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from dependency_injector.wiring import Provide , inject
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.mongo import provide_interview_mongo_db
from backend.data_access.mongo.home.home_stats_repository import HomeStatsRepository

# def get_home_stats_repository(
#     mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
# ) -> HomeStatsRepository:
#     return HomeStatsRepository(mongo_client)

@inject 
def get_home_stats_repository (
    db : AsyncIOMotorDatabase = Depends[provide_interview_mongo_db],
    factory = Provide[RepositoriesContainer.home_stats_repository_factory]
)-> HomeStatsRepository:
    return factory(db)