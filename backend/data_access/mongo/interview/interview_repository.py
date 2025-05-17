from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

class InterviewRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.db = mongo_client["interview_db"]

    async def insert_question_session(self, session_data: dict):
        return await self.db["questions"].insert_one(session_data)

    async def find_session_by_user_id(self, user_id: str):
        return await self.db["questions"].find_one({"user_id": user_id})

    async def find_session_by_session_id(self, session_id: int, user_id: str):
        query = {"session_id": session_id, "user_id": user_id}
        session = await self.db["questions"].find_one(query)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or unauthorized")
        return session

    async def insert_user_answer(self, answer_data: dict):
        return await self.db["answers"].insert_one(answer_data)

    async def find_latest_answer(self, session_id: int, user_id: str):
        return await self.db["answers"].find_one(
            {"session_id": session_id, "user_id": user_id},
            sort=[("question_index", -1)]
        )

    async def update_answer_feedback(self, session_id: int, user_id: str, question_index: int, feedback_data: dict):
        return await self.db["answers"].update_one(
            {"session_id": session_id, "user_id": user_id, "question_index": question_index},
            {"$set": feedback_data}
        )

    async def get_all_answers_with_scores(self, session_id: int, user_id: str):
        return await self.db["answers"].find(
            {"session_id": session_id, "user_id": user_id},
            {"similarity_score": 1, "question_index": 1}
        ).to_list(length=None)
