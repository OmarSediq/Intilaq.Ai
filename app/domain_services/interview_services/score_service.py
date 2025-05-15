from datetime import datetime, timezone
from app.utils.response_schemas import success_response, error_response
from app.data_access.mongo.mongo_services import (
    get_all_answers_with_scores,
    find_session_by_session_id
)
from app.domain_services.interview_services.validator_service import InterviewValidatorService

class InterviewScoreService:
    def __init__(self, validator: InterviewValidatorService):
        self.validator = validator
    async def calculate_score(self, session_id: int, user_id: str):
        is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        answers = await get_all_answers_with_scores(session_id, user_id)
        if not answers:
            return error_response(code=404, error_message="No answers with scores found for this session")

        scores = []
        question_scores = []

        for ans in answers:
            score = ans.get("similarity_score", 0)
            question_index = ans.get("question_index", -1)
            scores.append(score)
            question_scores.append({
                "question_index": question_index,
                "score": round(score, 2)
            })

        total_score = sum(scores)
        max_score = len(scores) * 10
        final_score = (total_score / max_score) * 100

        return success_response(code=200, data={
            "session_id": session_id,
            "answered_questions": len(scores),
            "final_score": round(final_score, 2),
            "question_scores": question_scores
        })

    async def end_session(self, session_id: int, user_id: str, db):
        is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        answers = await get_all_answers_with_scores(session_id, user_id)
        if not answers:
            return error_response(code=404, error_message="No answers with scores found for this session")

        scores = [ans.get("similarity_score", 0) for ans in answers]
        if not scores:
            return error_response(code=404, error_message="No similarity scores found")

        total_score = sum(scores)
        max_score = len(scores) * 10
        final_score = (total_score / max_score) * 100
        answered_questions = len(scores)

        session_results_collection = db["session_results"]
        await session_results_collection.insert_one({
            "session_id": session_id,
            "user_id": user_id,
            "final_score": round(final_score, 2),
            "total_questions": max_score // 10,
            "answered_questions": answered_questions,
            "accuracy": round((total_score / (answered_questions * 10)) * 100, 2),
            "status": "ended",
            "ended_at": datetime.now(timezone.utc)
        })

        session = await find_session_by_session_id(session_id, user_id)
        if not session:
            return error_response(code=404, error_message="Session data not found")

        user_summary_collection = db["user_home_summary"]
        existing_summary = await user_summary_collection.find_one({"user_id": user_id})

        if existing_summary:
            new_total_interviews = existing_summary["total_interviews"] + 1
            new_total_answers = existing_summary["total_answers"] + len(scores)
            new_avg_score = ((existing_summary["avg_score"] * existing_summary["total_interviews"]) + final_score) / new_total_interviews
            new_accuracy = ((existing_summary["accuracy"] * existing_summary["total_answers"]) + sum(scores)) / new_total_answers

            await user_summary_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "avg_score": round(new_avg_score, 2),
                        "accuracy": round(new_accuracy, 2),
                        "last_session": {
                            "session_id": session_id,
                            "job_title": session.get("job_title", "N/A"),
                            "final_score": round(final_score, 2),
                            "ended_at": datetime.now(timezone.utc)
                        },
                        "updated_at": datetime.now(timezone.utc)
                    },
                    "$inc": {
                        "total_interviews": 1,
                        "total_answers": len(scores)
                    }
                }
            )
        else:
            await user_summary_collection.insert_one({
                "user_id": user_id,
                "total_interviews": 1,
                "total_answers": len(scores),
                "avg_score": round(final_score, 2),
                "accuracy": round(sum(scores) / len(scores), 2),
                "last_session": {
                    "session_id": session_id,
                    "job_title": session.get("job_title", "N/A"),
                    "final_score": round(final_score, 2),
                    "ended_at": datetime.now(timezone.utc)
                },
                "updated_at": datetime.now(timezone.utc)
            })

        return success_response(code=200, data={
            "final_score": round(final_score, 2),
            "answered_questions": answered_questions,
            "message": "Session completed and evaluated successfully"
        })
