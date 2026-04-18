from backend.core.base_service import TraceableService
from motor.motor_asyncio import  AsyncIOMotorDatabase

class InterviewAnswerRepository(TraceableService): 
    def __init__(self  ,db: AsyncIOMotorDatabase):
        self.collection = db["answers"]


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

        