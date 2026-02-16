import uuid
from datetime import datetime, timezone

from backend.core.base_service import TraceableService
from backend.utils.response_schemas import success_response, error_response
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from backend.domain_services.ai_services.gemini_ai_service import  GeminiAIService

class HRInterviewService(TraceableService):
    def __init__(self, hr_repo: HRInterviewRepository , gemini_service : GeminiAIService):
        self.hr_repo = hr_repo
        self.gemini_service = gemini_service

    async def create_metadata(self, request, hr_id: int):
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
        await self.hr_repo.insert_interview(interview_data)

        ai_questions_raw = await self.gemini_service.generate_questions_for_hr(
            job_name=request.job_title,
            job_level=request.level,
            job_requirements=request.job_requirements or ""
        )
        questions = [q.strip() for q in ai_questions_raw.split("\n") if q.strip()]


        questions_with_answers = []
        for i, q in enumerate(questions):
            best_answer = await self.gemini_service.generate_best_answer(q)
            questions_with_answers.append({
                "index": i ,
                "question": q,
                "response_type": "text",
                "time_limit": None,
                "ideal_answer": best_answer
            })

        question_doc = {
            "interview_token": interview_token,
            "hr_id": hr_id,
            "questions": questions_with_answers,
            "created_at": datetime.now(timezone.utc)
        }

        await self.hr_repo.insert_questions(question_doc)

        return success_response(code=201, data={
            "message": "Interview metadata and AI questions created successfully.",
            "interview_token": interview_token,
            "ai_questions": [f"{i + 1}. {q['question']}" for i, q in enumerate(questions_with_answers)]
        })

    async def update_question(self, interview_token: str, index: int, update_data):
        doc = await self.hr_repo.find_question_doc(interview_token)
        if not doc:
            return error_response(code=404, error_message="Interview not found.")

        questions = doc.get("questions", [])
        if index < 0 or index >= len(questions):
            return error_response(code=404, error_message="Question index out of range.")

        existing = questions[index]

        new_question_text = (update_data.question_text or existing["question"]).strip()
        new_response_type = update_data.response_type or existing["response_type"]
        new_time_limit = update_data.time_limit if update_data.time_limit is not None else existing["time_limit"]

        if new_question_text != existing["question"]:
            new_ideal_answer = await self.gemini_service.generate_best_answer(new_question_text)
        else:
            new_ideal_answer = existing.get("ideal_answer")

        updated_fields = {
            "question": new_question_text,
            "response_type": new_response_type,
            "time_limit": new_time_limit,
            "ideal_answer": new_ideal_answer
        }

        await self.hr_repo.update_question_by_index(interview_token, index, updated_fields)

        return success_response(code=200, data={**existing, **updated_fields})

    async def get_all_basic_questions(self, interview_token: str):
        question_map = await self.hr_repo.get_all_basic_questions_by_token(interview_token)
        if not question_map:
            return error_response(code=404, error_message="No questions found for this token")

        return success_response(code=200, data={"questions": question_map})

    async def get_unified_answer_by_index(
            self,
            interview_token: str,
            user_email: str,
            index: int
    ):
        result = await self.hr_repo.get_unified_answer_by_index(
            interview_token=interview_token,
            user_email=user_email,
            index=index
        )

        if not result:
            return error_response(code=404, error_message="No answer found for given index.")

        return success_response(code=200, data=result)
