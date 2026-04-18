from backend.core.base_service import TraceableService
from motor.motor_asyncio import  AsyncIOMotorDatabase


class InterviewHomeSummaryRepository(TraceableService):
    def __init__(self , db: AsyncIOMotorDatabase):
        self.collection=db["user_home_summary"]
       

    async def find_user_summary(self, user_id: str):
        return await self.db["user_home_summary"].find_one({"user_id": user_id})

    async def update_user_summary(self, user_id: str, update_data: dict, inc_data: dict):
        return await self.db["user_home_summary"].update_one(
            {"user_id": user_id},
            {"$set": update_data, "$inc": inc_data}
        )

    async def insert_user_summary(self, data: dict):
        return await self.db["user_home_summary"].insert_one(data)
