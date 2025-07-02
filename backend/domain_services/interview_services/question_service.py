from backend.utils.response_schemas import success_response, error_response
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from backend.data_access.mongo.interview.interview_repository import InterviewRepository
from backend.data_access.redis.session_redis_repository import SessionRedisRepository
from backend.core.base_service import TraceableService
class InterviewQuestionService(TraceableService):
    def __init__(self, validator: InterviewValidatorService , repo_interview : InterviewRepository , repo_session : SessionRedisRepository) :
        self.validator = validator
        self.repo_interview = repo_interview
        self.repo_session = repo_session


    async def get_questions(self, session_id: int, user_id: str):
        is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        session = await self.repo_interview.find_session_by_session_id(session_id, user_id)
        questions_only = [q["question"] for q in session["questions"]]
        return success_response(code=200, data={"session_id": session_id, "questions": questions_only})

    async def get_next_question(self, session_id: int, user_id: str):
        is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        session = await self.repo_interview.find_session_by_session_id(session_id, user_id)
        current_index = await self.repo_session.get_current_question_index(session_id)
        questions = session["questions"]

        if current_index >= len(questions):
            return success_response(code=200, data={"message": "No more questions available."})

        question = questions[current_index]
        return success_response(code=200, data={
            "question": question["question"],
            "question_index": current_index
        })
