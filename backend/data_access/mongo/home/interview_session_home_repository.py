from motor.motor_asyncio import AsyncIOMotorDatabase

class InterviewSessionHomeRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.questions_collection = db["questions"]
        self.answers_collection = db["answers"]
        self.results_collection = db["session_results"]

    async def get_session_meta(self, session_id: int, user_id: int):
        return await self.questions_collection.find_one(
            {"session_id": session_id, "user_id": user_id},
            {"_id": 0, "job_title": 1, "level": 1, "created_at": 1, "questions": 1}
        )

    async def get_first_answer(self, session_id: int, user_id: int):
        return await self.answers_collection.find_one(
            {"session_id": session_id, "user_id": user_id, "question_index": 0},
            {"_id": 0, "answer_text": 1, "feedback": 1}
        )

    async def get_session_detail(self, session_id: int, user_id: int):
        return await self.questions_collection.find_one(
            {"session_id": session_id, "user_id": user_id},
            {"_id": 0, "questions": 1, "job_title": 1, "level": 1, "created_at": 1}
        )

    async def get_answers(self, session_id: int, user_id: int):
        cursor = self.answers_collection.find(
            {"session_id": session_id, "user_id": user_id},
            {"_id": 0, "question_index": 1, "answer_text": 1, "feedback": 1}
        )
        return await cursor.to_list(length=None)

    async def get_result_score(self, session_id: int, user_id: int):
        return await self.results_collection.find_one(
            {"session_id": session_id, "user_id": user_id},
            {"_id": 0, "final_score": 1}
        )
