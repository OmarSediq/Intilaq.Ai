from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from backend.core.base_service import TraceableService


class HRAnswerRepository(TraceableService):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["hr_answers"]


    async def create_session(self, interview_token: str, user_name: str, user_email: str, login_time: datetime):
        session_doc = {
            "interview_token": interview_token,
            "user_name": user_name,
            "user_email": user_email,
            "login_time": login_time,
            "status": "started",
            "answers": []
        }
        await self.collection.insert_one(session_doc)

    async def get_session_by_token(self, interview_token: str) -> Optional[dict]:
        return await self.collection.find_one({"interview_token": interview_token})

    async def get_answer_by_index(self, interview_token: str, index: int) -> Optional[dict]:
        result = await self.collection.find_one(
            {"interview_token": interview_token},
            {"answers": {"$elemMatch": {"question_index": index}}}
        )
        return result.get("answers", [None])[0]

    async def session_exists(self, interview_token: str) -> bool:
        return await self.collection.count_documents({"interview_token": interview_token}, limit=1) > 0

    async def add_answer(self, interview_token: str, answer_doc: dict):
        await self.collection.update_one(
            {"interview_token": interview_token},
            {"$push": {"answers": answer_doc}}
        )

    async def update_answer_by_index(self, interview_token: str, index: int, update_fields: dict):
        query = {"interview_token": interview_token, f"answers.{index}": {"$exists": True}}
        set_fields = {f"answers.{index}.{k}": v for k, v in update_fields.items()}

        result = await self.collection.update_one(query, {"$set": set_fields})
        if result.modified_count == 0:
            print(f"[WARNING] Answer at index {index} not updated.")

    async def get_answer_by_video_id(self, video_id: str) -> Optional[dict]:
        result = await self.collection.find_one(
            {"answers.video_file_id": video_id},
            {"answers.$": 1, "interview_token": 1}
        )
        if result and "answers" in result:
            return result["answers"][0]
        return None

    async def get_session_by_video_id(self, video_id: str) -> Optional[dict]:
        query = {
            "$or": [
                {"answers.video_file_id": video_id},
                {"answers.video_file_id": ObjectId(video_id)}
            ]
        }

        return await self.collection.find_one(query, {"interview_token": 1, "answers": 1})