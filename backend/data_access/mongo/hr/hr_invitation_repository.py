from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class HRInvitationRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.collection = mongo_client["hr_db"]["hr_interviews"]

    async def get_interview_by_token(self, interview_token: str) -> Optional[dict]:
        return await self.collection.find_one({"interview_token": interview_token})

    async def update_interview_metadata(self, interview_token: str, update_data: dict):
        return await self.collection.update_one(
            {"interview_token": interview_token},
            {"$set": update_data}
        )
