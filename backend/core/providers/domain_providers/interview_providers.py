from fastapi import Depends
from backend.data_access.mongo.interview.interview_repository import InterviewRepository
from backend.data_access.redis.session_redis_repository import SessionRedisRepository
from backend.domain_services.interview_services.session_service import InterviewSessionService
from backend.domain_services.interview_services.question_service import InterviewQuestionService
from backend.domain_services.interview_services.answer_service import InterviewAnswerService
from backend.domain_services.interview_services.feedback_service import InterviewFeedbackService
from backend.domain_services.interview_services.score_service import InterviewScoreService
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService

from backend.core.providers.data_access_providers.session_providers.session_redis_repository_provider import get_session_redis_repository
from backend.core.providers.data_access_providers.interview_providers.interview_repository_provider import get_interview_repository
from backend.core.providers.ai_providers.gemini_provider import get_gemini_ai_service

# ========== INTERVIEW PROVIDERS ==========

def get_validator_service(
    repo_interview: InterviewRepository = Depends(get_interview_repository),
    repo_session: SessionRedisRepository = Depends(get_session_redis_repository),
) -> InterviewValidatorService:
    return InterviewValidatorService(repo_interview, repo_session)


def get_interview_session_service(
    validator: InterviewValidatorService = Depends(get_validator_service),
    gemini_service: GeminiAIService = Depends(get_gemini_ai_service),
    repo_interview: InterviewRepository = Depends(get_interview_repository),
    repo_session: SessionRedisRepository = Depends(get_session_redis_repository),
) -> InterviewSessionService:
    return InterviewSessionService(validator, gemini_service, repo_interview, repo_session)


def get_interview_question_service(
    validator: InterviewValidatorService = Depends(get_validator_service),
    repo_interview: InterviewRepository = Depends(get_interview_repository),
    repo_session: SessionRedisRepository = Depends(get_session_redis_repository),
) -> InterviewQuestionService:
    return InterviewQuestionService(validator, repo_interview, repo_session)


def get_interview_answer_service(
    validator: InterviewValidatorService = Depends(get_validator_service),
    repo_interview: InterviewRepository = Depends(get_interview_repository),
    repo_session: SessionRedisRepository = Depends(get_session_redis_repository),
) -> InterviewAnswerService:
    return InterviewAnswerService(validator, repo_interview, repo_session)


def get_interview_feedback_service(
    validator: InterviewValidatorService = Depends(get_validator_service),
    gemini_service: GeminiAIService = Depends(get_gemini_ai_service),
    repo_interview: InterviewRepository = Depends(get_interview_repository),
) -> InterviewFeedbackService:
    return InterviewFeedbackService(validator, gemini_service, repo_interview)


def get_interview_score_service(
    validator: InterviewValidatorService = Depends(get_validator_service),
    repo_interview: InterviewRepository = Depends(get_interview_repository),
) -> InterviewScoreService:
    return InterviewScoreService(validator, repo_interview)
