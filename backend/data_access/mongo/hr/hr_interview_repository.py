from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
import uuid

class HRInterviewRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.interviews = self.db["hr_interviews"]
        self.questions = self.db["hr_interview_questions"]
        self.answers =  self.db["hr_answers"]

    async def insert_interview(self, interview_data: dict):
        return await self.interviews.insert_one(interview_data)

    async def insert_questions(self, question_doc: dict):
        return await self.questions.insert_one(question_doc)

    async def find_question_doc(self, interview_token: str):
        return await self.questions.find_one({"interview_token": interview_token})

    async def update_question_by_index(self, interview_token: str, index: int, updated_fields: dict):

        updated_fields.pop("index", None)


        set_fields = {f"questions.{index}.{key}": value for key, value in updated_fields.items()}

        return await self.questions.update_one(
            {"interview_token": interview_token},
            {"$set": set_fields}
        )

    async def insert_interview_metadata(self, request, hr_id: int) -> str:
        interview_token = uuid.uuid4().hex
        interview_data = {
            "interview_token": interview_token,
            "job_title": request.job_title,
            "level": request.level,
            "job_requirements": request.job_requirements,
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
                    "index": i,
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


    async def get_question_by_token_and_index(self, interview_token: str, index: int) -> Optional[dict]:
        pipeline = [
            {"$match": {"interview_token": interview_token}},
            {"$unwind": "$questions"},
            {"$match": {"questions.index": index}},
            {"$project": {
                "_id": 0,
                "question": "$questions.question",
                "ideal_answer": "$questions.ideal_answer",
                "response_type": "$questions.response_type",
                "time_limit": "$questions.time_limit"
            }}
        ]
        cursor = self.questions.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0] if result else None

    async def get_text_question_and_user_answer(
            self,
            interview_token: str,
            index: int,
            user_email: str
    ) -> Optional[dict]:
        pipeline_question = [
            {"$match": {"interview_token": interview_token}},
            {"$unwind": "$questions"},
            {"$match": {
                "questions.index": index,
                "questions.response_type": {"$eq": "text"}
            }},
            {"$project": {
                "_id": 0,
                "question": "$questions.question",
                "ideal_answer": "$questions.ideal_answer",
                "time_limit": "$questions.time_limit",  # ✅ أضف هذا السطر
                "index": "$questions.index"
            }},
            {"$limit": 1}
        ]
        question_result = await self.questions.aggregate(pipeline_question).to_list(length=1)
        if not question_result:
            return None

        pipeline_answer = [
            {"$match": {
                "interview_token": interview_token,
                "user_email": user_email
            }},
            {"$unwind": "$answers"},
            {"$match": {
                "answers.question_index": index,
                "answers.response_type": {"$eq": "text"}
            }},
            {"$project": {
                "_id": 0,
                "answer_text": "$answers.answer_text"
            }},
            {"$limit": 1}
        ]
        answer_result = await self.answers.aggregate(pipeline_answer).to_list(length=1)
        if not answer_result:
            return None

        return {
            "question": question_result[0]["question"],
            "ideal_answer": question_result[0]["ideal_answer"],
            "time_limit": question_result[0].get("time_limit"),
            "answer_text": answer_result[0]["answer_text"],
            "index": index
        }

    async def get_by_token(self, interview_token: str):
        return await self.interviews.find_one({"interview_token": interview_token})

    async def get_all_basic_questions_by_token(self, interview_token: str) -> dict:
        doc = await self.questions.find_one({"interview_token": interview_token})
        if not doc:
            return {}

        questions = doc.get("questions", [])
        return {
            str(q["index"]): {
                "question": q.get("question"),
                "response_type": q.get("response_type"),
                "time_limit": q.get("time_limit")
            }
            for q in questions if "index" in q
        }

    async def get_unified_answer_by_index(
            self,
            interview_token: str,
            user_email: str,
            index: int
    ) -> Optional[dict]:

        question_pipeline = [
            {"$match": {"interview_token": interview_token}},
            {"$unwind": "$questions"},
            {"$match": {"questions.index": index}},
            {"$project": {
                "_id": 0,
                "index": "$questions.index",
                "question": "$questions.question",
                "ideal_answer": "$questions.ideal_answer",
                "response_type": "$questions.response_type",
                "time_limit": "$questions.time_limit"
            }},
            {"$limit": 1}
        ]
        question_result = await self.questions.aggregate(question_pipeline).to_list(length=1)
        if not question_result:
            raise HTTPException(status_code=404, detail="Question not found.")

        question_data = question_result[0]


        answer_pipeline = [
            {"$match": {
                "interview_token": interview_token,
                "user_email": user_email
            }},
            {"$unwind": "$answers"},
            {"$match": {"answers.question_index": index}},
            {"$project": {
                "_id": 0,
                "response_type": "$answers.response_type",
                "answer_text": "$answers.answer_text",
                "video_file_id": "$answers.video_file_id",
                "transcript": "$answers.transcript"
            }},
            {"$limit": 1}
        ]
        answer_result = await self.answers.aggregate(answer_pipeline).to_list(length=1)
        if not answer_result:
            raise HTTPException(status_code=404, detail="Answer not found.")

        answer_data = answer_result[0]


        unified = {
            "index": index,
            "response_type": question_data.get("response_type"),
            "question": question_data.get("question"),
            "ideal_answer": question_data.get("ideal_answer"),
            "time_limit": question_data.get("time_limit"),
        }

        if question_data["response_type"] == "text":
            unified["answer_text"] = answer_data.get("answer_text")
        elif question_data["response_type"] == "video":
            unified["video_file_id"] = answer_data.get("video_file_id")
            unified["transcript"] = answer_data.get("transcript")

        return unified
