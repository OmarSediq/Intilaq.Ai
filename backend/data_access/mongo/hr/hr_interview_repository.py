from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
import uuid

class HRInterviewRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.db = mongo_client["hr_db"]
        self.interviews = self.db["hr_interviews"]
        self.questions = self.db["hr_interview_questions"]

    async def insert_interview(self, interview_data: dict):
        return await self.interviews.insert_one(interview_data)

    async def insert_questions(self, question_doc: dict):
        return await self.questions.insert_one(question_doc)

    async def find_question_doc(self, interview_token: str):
        return await self.questions.find_one({"interview_token": interview_token})

    async def update_question_by_index(self, interview_token: str, index: int, updated_data: dict):
        return await self.questions.update_one(
            {"interview_token": interview_token},
            {"$set": {f"questions.{index}": updated_data}}
        )

    async def insert_interview_metadata(self, request, hr_id: int) -> str:
        interview_token = uuid.uuid4().hex
        interview_data = {
            "interview_token": interview_token,
            "job_title": request.job_title,
            "level": request.level,
            "job_requirements": request.job_requirements,
            "specific_date": request.specific_date,
            "date_range": request.date_range,
            "time": request.time,
            "hr_id": hr_id,
            "created_at": datetime.now(timezone.utc)
        }
        await self.interviews.insert_one(interview_data)
        return interview_token

    async def insert_interview_questions(self, interview_token: str, hr_id: int, questions: list[str]):
        question_doc = {
            "interview_token": interview_token,
            "hr_id": hr_id,
            "questions": [
                {
                    "index": i + 1,
                    "text": q,
                    "response_type": "text",
                    "time_limit": None
                } for i, q in enumerate(questions)
            ],
            "created_at": datetime.now(timezone.utc)
        }
        await self.questions.insert_one(question_doc)

    async def update_interview_question(self, interview_token: str, index: int, update_data):
        document = await self.questions.find_one({"interview_token": interview_token})
        if not document:
            raise HTTPException(status_code=404, detail="Interview not found.")

        questions = document.get("questions", [])
        if index < 0 or index >= len(questions):
            raise HTTPException(status_code=404, detail="Question index out of range.")

        questions[index] = {
            "index": index,
            "text": update_data.question_text,
            "response_type": update_data.response_type,
            "time_limit": update_data.time_limit,
        }

        await self.questions.update_one(
            {"interview_token": interview_token},
            {"$set": {f"questions.{index}": questions[index]}}
        )
        return questions[index]

    async def get_question_by_index(self, interview_token: str, index: int) -> dict:
        doc = await self.questions.find_one({"interview_token": interview_token})
        if not doc:
            raise ValueError(f"No questions found for token: {interview_token}")

        questions = doc.get("questions", [])
        if index >= len(questions):
            raise ValueError(f"No question found at index: {index}")

        return questions[index]