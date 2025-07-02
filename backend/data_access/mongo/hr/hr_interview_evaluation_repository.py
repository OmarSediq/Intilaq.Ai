from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.core.base_service import TraceableService


class HRInterviewEvaluationRepository(TraceableService):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.answers_collection = db["hr_answers"]

    async def get_video_file_by_token_and_index(self, interview_token: str, user_email: str, index: int) -> Optional[
        dict]:
        pipeline = [
            {"$match": {
                "interview_token": interview_token,
                "user_email": user_email
            }},
            {"$unwind": "$answers"},
            {"$match": {
                "answers.response_type": "video",
                "answers.question_index": index
            }},
            {"$limit": 1},
            {"$project": {
                "_id": 0,
                "video_file_id": "$answers.video_file_id"
            }}
        ]
        cursor = self.answers_collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0] if result else None

    async def get_answer_type_indexes(self, interview_token: str, user_email: str) -> dict:
        cursor = self.answers_collection.aggregate([
            {"$match": {
                "interview_token": interview_token,
                "user_email": user_email
            }},
            {"$project": {
                "video_indexes": {
                    "$map": {
                        "input": {
                            "$filter": {
                                "input": "$answers",
                                "as": "ans",
                                "cond": {"$eq": ["$$ans.response_type", "video"]}
                            }
                        },
                        "as": "video",
                        "in": "$$video.question_index"
                    }
                },
                "text_indexes": {
                    "$map": {
                        "input": {
                            "$filter": {
                                "input": "$answers",
                                "as": "ans",
                                "cond": {"$eq": ["$$ans.response_type", "text"]}
                            }
                        },
                        "as": "text",
                        "in": "$$text.question_index"
                    }
                }
            }}
        ])
        result = await cursor.to_list(length=1)
        return result[0] if result else {}

