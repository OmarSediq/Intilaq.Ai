from datetime import datetime, timezone

from backend.core.base_service import TraceableService
from backend.utils.response_schemas import success_response, error_response
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from backend.data_access.mongo.interview.interview_repository import InterviewRepository

class InterviewScoreService(TraceableService):
    def __init__(self, validator: InterviewValidatorService, repo_interview: InterviewRepository):
        self.validator = validator
        self.repo_interview = repo_interview

    async def calculate_score(self, session_id: int, user_id: str):
        is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        answers = await self.repo_interview.get_all_answers_with_scores(session_id, user_id)
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

    async def end_session(self, session_id: int, user_id: str):
        is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        answers = await self.repo_interview.get_all_answers_with_scores(session_id, user_id)
        if not answers:
            return error_response(code=404, error_message="No answers with scores found for this session")

        scores = [ans.get("similarity_score", 0) for ans in answers]
        if not scores:
            return error_response(code=404, error_message="No similarity scores found")

        total_score = sum(scores)
        max_score = len(scores) * 10
        final_score = (total_score / max_score) * 100
        answered_questions = len(scores)

        # حفظ نتائج الجلسة في session_results
        await self.repo_interview.save_session_result({
            "session_id": session_id,
            "user_id": user_id,
            "final_score": round(final_score, 2),
            "total_questions": max_score // 10,
            "answered_questions": answered_questions,
            "accuracy": round((total_score / (answered_questions * 10)) * 100, 2),
            "status": "ended",
            "ended_at": datetime.now(timezone.utc)
        })

        session = await self.repo_interview.find_session_by_session_id(session_id, user_id)
        if not session:
            return error_response(code=404, error_message="Session data not found")

        existing_summary = await self.repo_interview.find_user_summary(user_id)

        if existing_summary:
            new_total_interviews = existing_summary["total_interviews"] + 1
            new_total_answers = existing_summary["total_answers"] + len(scores)
            new_avg_score = (
                (existing_summary["avg_score"] * existing_summary["total_interviews"]) + final_score
            ) / new_total_interviews
            new_accuracy = (
                (existing_summary["accuracy"] * existing_summary["total_answers"]) + sum(scores)
            ) / new_total_answers

            await self.repo_interview.update_user_summary(
                user_id=user_id,
                update_data={
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
                inc_data={
                    "total_interviews": 1,
                    "total_answers": len(scores)
                }
            )
        else:
            await self.repo_interview.insert_user_summary({
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
