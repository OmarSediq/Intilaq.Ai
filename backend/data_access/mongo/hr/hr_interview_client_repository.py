from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from backend.core.base_service import TraceableService


class HRAnswerRepository(TraceableService):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["hr_answers"]


    async def create_session(self, interview_token: str, user_name: str, user_email: str, login_time: datetime , hr_id: int):
        session_doc = {
            "interview_token": interview_token,
            "user_name": user_name,
            "user_email": user_email,
            "login_time": login_time,
            "review_status": "pending",
             "hr_id": hr_id,
            "answers": []
        }
        await self.collection.insert_one(session_doc)

    async def get_session_by_token(self, interview_token: str) -> Optional[dict]:
        return await self.collection.find_one({"interview_token": interview_token})

    async def get_answer_by_index(self, interview_token: str, user_email: str, index: int) -> Optional[dict]:
        result = await self.collection.find_one(
            {
                "interview_token": interview_token,
                "user_email": user_email,
            },
            {
                "answers": {"$elemMatch": {"question_index": index}}
            }
        )
        return result.get("answers", [None])[0] if result else None

    async def session_exists(self, interview_token: str) -> bool:
        return await self.collection.count_documents({"interview_token": interview_token}, limit=1) > 0

    async def session_exists_for_create(self, interview_token: str, user_email: str) -> bool:
        return await self.collection.count_documents({
            "interview_token": interview_token,
            "user_email": user_email
        }, limit=1) > 0

    async def add_answer(self, interview_token: str, answer_doc: dict):
        await self.collection.update_one(
            {"interview_token": interview_token},
            {"$push": {"answers": answer_doc}}
        )

    async def update_answer_by_index(
            self,
            interview_token: str,
            user_email: str,
            question_index: int,
            update_fields: dict,
    ):
        set_ops = {f"answers.$.{k}": v for k, v in update_fields.items()}
        result = await self.collection.update_one(
            {
                "interview_token": interview_token,
                "user_email": user_email,
                "answers.question_index": question_index
            },
            {"$set": set_ops}
        )

        if result.modified_count == 0:
            print(f"[INFO] No existing answer at q{question_index}; pushing new one.")
            answer_doc = {"question_index": question_index, **update_fields}
            await self.collection.update_one(
                {"interview_token": interview_token, "user_email": user_email},
                {"$push": {"answers": answer_doc}}
            )

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
        return await self.collection.find_one(query,{"interview_token": 1, "user_email": 1, "answers": 1})

    async def get_session_by_token_and_email(self, interview_token: str, user_email: str):
        return await self.collection.find_one({
            "interview_token": interview_token,
            "user_email": user_email
        })

    async def add_answer_to_user(self, interview_token: str, user_email: str, answer_doc: dict):
        question_index = answer_doc.get("question_index")
        if question_index is None:
            raise ValueError("answer_doc must include 'question_index'")

        await self.collection.update_one(
            {
                "interview_token": interview_token,
                "user_email": user_email
            },
            {
                "$set": {
                    f"answers.{question_index}": answer_doc
                }
            }
        )

    async def set_overall_score(self, interview_token: str, user_email: str, score: float):
        await self.collection.update_one(
            {"interview_token": interview_token, "user_email": user_email},
            {"$set": {"overall_score": score}}
        )

    async def set_review_status(self, interview_token: str, user_email: str, status: str):

        if status not in ("accepted", "rejected"):
            raise ValueError("Invalid review status")

        result = await self.collection.update_one(
            {
                "interview_token": interview_token,
                "user_email": user_email,
                "review_status": {"$exists": True}
            },
            {"$set": {"review_status": status}}
        )

        if result.matched_count == 0:
            raise ValueError(
                "Session not found or `review_status` field missing — nothing updated."
            )
