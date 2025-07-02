from motor.motor_asyncio import AsyncIOMotorClient

class HomeStatsRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.collection = mongo_client["interview_db"]["user_home_summary"]

    async def fetch_user_summary(self, user_id: int) -> dict:
        return await self.collection.find_one(
            {"user_id": user_id},
            {"_id": 0, "total_interviews": 1, "total_answers": 1, "avg_score": 1, "accuracy": 1}
        ) or {}
