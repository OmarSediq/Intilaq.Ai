from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase ,  AsyncIOMotorGridFSBucket


class HRAnswerRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["hr_answers"]
        self.gridfs_bucket = AsyncIOMotorGridFSBucket(db)

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

    async def upload_video(self, filename: str, file_stream) -> str:
        video_id = await self.gridfs_bucket.upload_from_stream(filename, file_stream)
        return str(video_id)

    async def add_answer(self, interview_token: str, answer_doc: dict):
        await self.collection.update_one(
            {"interview_token": interview_token},
            {"$push": {"answers": answer_doc}}
        )