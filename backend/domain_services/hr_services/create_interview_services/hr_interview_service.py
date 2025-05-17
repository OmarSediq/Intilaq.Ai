import uuid
from datetime import datetime, timezone
from backend.utils.response_schemas import success_response, error_response
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from backend.domain_services.ai_services.gemini_ai_service import  GeminiAIService

class HRInterviewService:
    def __init__(self, repository: HRInterviewRepository , gemini_service : GeminiAIService):
        self.repo = repository
        self.gemini_service = gemini_service

    async def create_metadata(self, request, hr_id: int):
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
        await self.repo.insert_interview(interview_data)

        ai_questions_raw = await self.gemini_service.generate_questions_for_hr(
            job_name=request.job_title,
            job_level=request.level,
            job_requirements=request.job_requirements or ""
        )
        questions = [q.strip() for q in ai_questions_raw.split("\n") if q.strip()]
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

        await self.repo.insert_questions(question_doc)

        return success_response(code=201, data={
            "message": "Interview metadata and AI questions created successfully.",
            "interview_token": interview_token,
            "ai_questions": [f"{i+1}. {q}" for i, q in enumerate(questions)]
        })

    async def update_question(self, interview_token: str, index: int, update_data):
        doc = await self.repo.find_question_doc(interview_token)
        if not doc:
            return error_response(code=404, error_message="Interview not found.")

        questions = doc.get("questions", [])
        if index < 0 or index >= len(questions):
            return error_response(code=404, error_message="Question index out of range.")

        updated_question = {
            "index": index,
            "text": update_data.question_text,
            "response_type": update_data.response_type,
            "time_limit": update_data.time_limit,
        }

        await self.repo.update_question_by_index(interview_token, index, updated_question)

        return success_response(code=200, data=updated_question)
