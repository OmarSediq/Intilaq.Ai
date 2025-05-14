from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.redis_services import get_user_session_ids

from app.utils.response_schemas import success_response, error_response
from app.services.interview_services.validator_service import InterviewValidatorService

class InterviewSessionServiceHome:
    def __init__(self, mongo_client: AsyncIOMotorClient , validator: InterviewValidatorService ):
        self.db = mongo_client["interview_db"]
        self.validator = validator
    

    async def get_sessions(self, user_id: int):
        try:
            session_ids = await get_user_session_ids(user_id)
            if not session_ids:
                return success_response(code=200, data={"sessions": []})

            sessions_data = []

            for session_id in session_ids:
                session_doc = await self.db["questions"].find_one(
                    {"session_id": session_id, "user_id": user_id},
                    {"_id": 0, "job_title": 1, "level": 1, "created_at": 1, "questions": 1}
                )
                if not session_doc or not session_doc.get("questions"):
                    continue

                answer_doc = await self.db["answers"].find_one(
                    {"session_id": session_id, "user_id": user_id, "question_index": 0},
                    {"_id": 0, "answer_text": 1, "feedback": 1}
                )

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
            is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
            if not is_valid:
                return error_response(code=404, error_message="Session not found or unauthorized")

            session_doc = await self.db["questions"].find_one(
                {"session_id": session_id, "user_id": user_id},
                {"_id": 0, "questions": 1, "job_title": 1, "level": 1, "created_at": 1}
            )
            if not session_doc:
                return error_response(code=404, error_message="Session not found")

            answers_cursor = self.db["answers"].find(
                {"session_id": session_id, "user_id": user_id},
                {"_id": 0, "question_index": 1, "answer_text": 1, "feedback": 1}
            )
            answers = await answers_cursor.to_list(length=None)
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

            result_doc = await self.db["session_results"].find_one(
                {"session_id": session_id, "user_id": user_id},
                {"_id": 0, "final_score": 1}
            )

            return success_response(code=200, data={
                "session_id": session_id,
                "job_title": session_doc.get("job_title"),
                "level": session_doc.get("level"),
                "created_at": session_doc.get("created_at").isoformat(),
                "questions": session_questions,
                "final_score": result_doc.get("final_score") if result_doc else None
            })

        except Exception as e:
            return error_response(code=500, error_message=f"Details fetch error: {str(e)}")
