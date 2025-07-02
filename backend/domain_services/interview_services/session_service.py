from datetime import datetime, timezone
import random
import asyncio

from backend.core.base_service import TraceableService
from backend.utils.response_schemas import success_response, error_response
from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from backend.data_access.mongo.interview.interview_repository import InterviewRepository
from backend.data_access.redis.session_redis_repository import SessionRedisRepository

class InterviewSessionService(TraceableService):
    def __init__(self, validator: InterviewValidatorService , gemini_service : GeminiAIService , repo_interview : InterviewRepository , repo_session : SessionRedisRepository):
        self.validator = validator
        self.gemini_service = gemini_service
        self.repo_interview = repo_interview
        self.repo_session = repo_session

    async def create_session(self, job_data, user):
        try:
            ai_questions = await self.gemini_service.generate_interview_questions(job_data.job_title, job_data.level, job_data.description)
            if not ai_questions:
                return error_response(code=400, error_message="No questions generated")

            questions_list = [q.strip() for q in ai_questions.split("\n") if q.strip()]
            session_id = random.randint(100000, 999999)

            best_model_answers = await asyncio.gather(
                *[self.gemini_service.generate_best_answer(q) for q in questions_list]
            )

            questions_with_answers = [
                {"question_index": idx, "question": q, "best_model_answer": a}
                for idx, (q, a) in enumerate(zip(questions_list, best_model_answers))
            ]

            session_data = {
                "session_id": session_id,
                "user_id": user["user_id"],
                "job_title": job_data.job_title,
                "level": job_data.level,
                "questions": questions_with_answers,
                "current_question_index": 0,
                "created_at": datetime.now(timezone.utc)
            }

            await self.repo_interview.insert_question_session(session_data)
            await self.repo_session.add_user_session_id(user["user_id"], session_id)
            await self.repo_session.set_current_question_index(session_id, 0)

            return success_response(code=201, data={"message": "Interview session created", "session_id": session_id})
        
        except Exception as e:
            return error_response(code=500, error_message=f"Error creating interview session: {str(e)}")

    async def start_session(self, session_id: int, user_id: str):
        is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        await self.repo_session.set_session_status(session_id, "active")
        await self.repo_session.set_current_question_index(session_id, 0)

        return success_response(code=200, data={"message": "Session started successfully", "session_id": session_id})
