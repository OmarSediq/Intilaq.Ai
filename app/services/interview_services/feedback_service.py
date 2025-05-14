from app.utils.response_schemas import success_response, error_response
from app.services.mongo_services import find_session_by_session_id, find_latest_answer, update_answer_feedback
from app.services.ai_services import generate_feedback, analyze_answer
from app.services.interview_services.validator_service import InterviewValidatorService

class InterviewFeedbackService:
    def __init__(self, validator: InterviewValidatorService):
        self.validator = validator
    async def get_feedback(self, session_id: int, question_index: int, user_id: str):
        is_valid = await self.validator. validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        latest_answer = await find_latest_answer(session_id, user_id)
        if not latest_answer:
            return error_response(code=404, error_message="User answer not found")

        session = await find_session_by_session_id(session_id, user_id)
        question_data = session["questions"][question_index]
        user_answer = latest_answer["answer_text"]
        ideal_answer = question_data.get("best_model_answer", "N/A")
        question_text = question_data["question"]

        feedback = generate_feedback(user_answer, question_text, ideal_answer)
        similarity_score = analyze_answer(user_answer, ideal_answer)

        await update_answer_feedback(session_id, user_id, question_index, {
            "feedback": feedback,
            "similarity_score": similarity_score
        })

        return success_response(code=200, data={
            "question": question_text,
            "user_answer": user_answer,
            "ideal_answer": ideal_answer,
            **feedback,
            "similarity_score": similarity_score
        })
