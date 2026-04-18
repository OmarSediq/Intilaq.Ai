from backend.core.base_service import TraceableService
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

class InterviewRepository (TraceableService):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["questions"]

    async def insert_question_session(self, session_data: dict):
        return await self.collection.insert_one(session_data)

    async def find_session_by_user_id(self, user_id: str):
        return await self.collection.find_one({"user_id": user_id})

    async def find_session_by_session_id(self, session_id: int, user_id: str):
        query = {
            "session_id": session_id,
            "user_id": int(user_id)
        }
        session = await self.collection.find_one(query)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or unauthorized")
        return session

   