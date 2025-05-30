from datetime import datetime, timezone
from fastapi import UploadFile
from backend.utils.response_schemas import success_response, error_response
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from backend.data_access.mongo.interview.interview_repository import InterviewRepository
from backend.data_access.redis.session_redis_repository import SessionRedisRepository
from backend.domain_services.ai_services.whisper_transcriber_service import WhisperTranscriberService
from backend.core.base_service import TraceableService

class InterviewAnswerService(TraceableService):
    def __init__(
        self,
        validator: InterviewValidatorService,
        repo_interview: InterviewRepository,
        repo_session: SessionRedisRepository,
        whisper_service: WhisperTranscriberService
    ):
        self.validator = validator
        self.repo_interview = repo_interview
        self.repo_session = repo_session
        self.whisper_service = whisper_service

    async def submit_answer(self, session_id: int, file: UploadFile, user_id: str):
        is_valid = await self.validator.validate_and_sync_session(session_id, user_id)
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")

        session = await self.repo_interview.find_session_by_session_id(session_id, user_id)
        current_index = await self.repo_session.get_current_question_index(session_id)

        if current_index >= len(session["questions"]):
            return error_response(code=400, error_message="No more questions remaining")

        try:
            result = await self.whisper_service.transcribe_audio(file)
            transcribed_text = result.get("text", "").strip()
            whisper_error = result.get("error")

            if not transcribed_text:

                error_msg = whisper_error or "Empty transcription"
                is_user_error = any(keyword in error_msg.lower() for keyword in [
                    "unsupported", "invalid", "empty", "format", "parse", "transcription"
                ])

                return error_response(
                    code=400 if is_user_error else 500,
                    error_message=f"Whisper error: {error_msg}"
                )

            await self.repo_interview.insert_user_answer({
                "session_id": session_id,
                "user_id": user_id,
                "question_index": current_index,
                "answer_text": transcribed_text,
                "timestamp": datetime.now(timezone.utc)
            })

            await self.repo_session.add_completed_question(session_id, current_index)
            await self.repo_session.set_current_question_index(session_id, current_index + 1)

            return success_response(code=200, data={
                "message": "Answer submitted successfully",
                "question_index": current_index,
                "transcribed_text": transcribed_text
            })

        except Exception as e:
            return error_response(code=500, error_message=f"Speech-to-Text failed: {str(e)}")
