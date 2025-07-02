from datetime import datetime
from http.client import HTTPException

from backend.utils.response_schemas import success_response, error_response
from backend.data_access.redis.session_redis_repository import SessionRedisRepository
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from backend.data_access.mongo.home.interview_session_home_repository import InterviewSessionHomeRepository


class InterviewSessionHomeService:
    def __init__(
        self,
        repository: InterviewSessionHomeRepository,
        redis_repo: SessionRedisRepository,
        validator: InterviewValidatorService
    ):
        self.repo = repository
        self.redis = redis_repo
        self.validator = validator

    async def get_sessions(self, user_id: int):
        try:
            session_ids = await self.redis.get_user_session_ids(str(user_id))
            if not session_ids:
                return success_response(code=200, data={"sessions": []})

            sessions_data = []

            for session_id in session_ids:
                session_doc = await self.repo.get_session_meta(session_id, user_id)
                if not session_doc or not session_doc.get("questions"):
                    continue

                answer_doc = await self.repo.get_first_answer(session_id, user_id)

                sessions_data.append({
                    "session_id": session_id,
                    "job_title": session_doc.get("job_title", "Unknown"),
                    "level": session_doc.get("level", "Unknown"),
                    "created_at": session_doc.get("created_at").isoformat() if session_doc.get("created_at") else None,
                    "question": session_doc["questions"][0].get("question"),
                    "answer_text": answer_doc.get("answer_text") if answer_doc else None,
                    "feedback": answer_doc.get("feedback") if answer_doc else None,
                })

            return success_response(code=200, data={"sessions": sessions_data})
        except Exception as e:
            return error_response(code=500, error_message=f"Session fetch error: {str(e)}")

    async def get_session_details(self, session_id: int, user_id: int):
        try:
            is_valid = await self.validator.validate_and_sync_session(session_id, str(user_id))
            if not is_valid:
                return error_response(code=404, error_message="Session not found or unauthorized")

            session_doc = await self.repo.get_session_detail(session_id, user_id)
            if not session_doc:
                return error_response(code=404, error_message="Session not found")

            answers = await self.repo.get_answers(session_id, user_id)
            answers_map = {a["question_index"]: a for a in answers}

            session_questions = []
            for q in session_doc["questions"]:
                index = q["question_index"]
                session_questions.append({
                    "question_index": index,
                    "question": q.get("question"),
                    "best_model_answer": q.get("best_model_answer"),
                    "user_answer": answers_map.get(index, {}).get("answer_text"),
                    "feedback": answers_map.get(index, {}).get("feedback")
                })

            result_doc = await self.repo.get_result_score(session_id, user_id)

            return success_response(code=200, data={
                "session_id": session_id,
                "job_title": session_doc.get("job_title"),
                "level": session_doc.get("level"),
                "created_at": session_doc.get("created_at").isoformat(),
                "questions": session_questions,
                "final_score": result_doc.get("final_score") if result_doc else None
            })


        except HTTPException as http_exc:

            raise http_exc

        except Exception as e:

            return error_response(code=500, error_message=f"Unexpected error: {str(e)}")

