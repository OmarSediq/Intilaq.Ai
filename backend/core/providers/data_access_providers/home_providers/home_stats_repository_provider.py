from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.providers.infra_providers import get_mongo_client
from backend.data_access.mongo.home.home_stats_repository import HomeStatsRepository

def get_home_stats_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> HomeStatsRepository:
    return HomeStatsRepository(mongo_client)
