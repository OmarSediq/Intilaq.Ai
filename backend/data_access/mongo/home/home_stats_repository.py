# backend/data_access/mongo/home/home_stats_repository.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

class HomeStatsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["user_home_summary"]

    async def fetch_user_summary(self, user_id: int) -> dict:
        result = await self.collection.find_one(
            {"user_id": user_id},
            {"_id": 0, "total_interviews": 1, "total_answers": 1, "avg_score": 1, "accuracy": 1}
        )
        return result or {}
