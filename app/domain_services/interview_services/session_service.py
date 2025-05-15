from datetime import datetime, timezone
import random
import asyncio
from app.utils.response_schemas import success_response, error_response
from app.domain_services.ai_services import generate_interview_questions, generate_best_model_answer
from app.data_access.redis.redis_services import add_user_session_id, set_current_question_index, set_session_status
from app.data_access.mongo.mongo_services import insert_question_session
from app.domain_services.interview_services.validator_service import InterviewValidatorService


class InterviewSessionService:
    def __init__(self, validator: InterviewValidatorService):
        self.validator = validator
    async def create_session(self, job_data, user):
        try:
            ai_questions = await generate_interview_questions(job_data.job_title, job_data.level, job_data.description)
            if not ai_questions:
                return error_response(code=400, error_message="No questions generated")

            questions_list = [q.strip() for q in ai_questions.split("\n") if q.strip()]
            session_id = random.randint(100000, 999999)

            best_model_answers = await asyncio.gather(
                *[generate_best_model_answer(q) for q in questions_list]
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

            await insert_question_session(session_data)
            await add_user_session_id(user["user_id"], session_id)
            await set_current_question_index(session_id, 0)

            return success_response(code=201, data={"message": "Interview session created", "session_id": session_id})
        
        except Exception as e:
            return error_response(code=500, error_message=f"Error creating interview session: {str(e)}")

    async def start_session(self, session_id: int, user_id: str):
        is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        await set_session_status(session_id, "active")
        await set_current_question_index(session_id, 0)

        return success_response(code=200, data={"message": "Session started successfully", "session_id": session_id})
