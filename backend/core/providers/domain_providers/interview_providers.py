from fastapi import Depends
from backend.core.containers.application_container import ApplicationContainer
from backend.domain_services.interview_services.session_service import InterviewSessionService
from backend.domain_services.interview_services.question_service import InterviewQuestionService
from backend.domain_services.interview_services.answer_service import InterviewAnswerService
from backend.domain_services.interview_services.feedback_service import InterviewFeedbackService
from backend.domain_services.interview_services.score_service import InterviewScoreService
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from dependency_injector.wiring import inject , Provide 

@inject
def get_validator_service(
    repo_interview = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider]),
    repo_session = Depends(Provide[ApplicationContainer.repos.session_redis_repository_factory.provider])
)-> InterviewValidatorService: 
    return InterviewValidatorService(repo_interview , repo_session)


@inject
def get_interview_session_service(
    validator = Depends(Provide[ApplicationContainer.service.validator_service]),
    gemini_service = Depends(Provide[ApplicationContainer.ai.gemini_service]),
    repo_interview = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider]),
    repo_session = Depends(Provide[ApplicationContainer.repos.session_redis_repository_factory.provider])
)-> InterviewSessionService:
    return InterviewSessionService(validator , gemini_service , repo_interview , repo_session)

@inject
def get_interview_question_service(
    validator = Depends(Provide[ApplicationContainer.service.validator_service]),
    repo_interview = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider]),
    repo_session = Depends(Provide[ApplicationContainer.repos.session_redis_repository_factory.provider])
)-> InterviewQuestionService:
    return InterviewQuestionService(validator, repo_interview , repo_session)


@inject
def get_interview_answer_service(
    validator =Depends( Provide[ApplicationContainer.service.validator_service]),
    whisper_service = Depends(Provide[ApplicationContainer.ai.whisper_transcriber]),
    repo_interview = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider]),
    repo_session = Depends(Provide[ApplicationContainer.repos.session_redis_repository_factory.provider])
)-> InterviewAnswerService:
    return InterviewAnswerService(validator , repo_interview , repo_session , whisper_service)

@inject
def get_interview_feedback_service(
    validator = Depends(Provide[ApplicationContainer.service.validator_service]),
    gemini_service = Depends(Provide[ApplicationContainer.ai.gemini_service]),
    repo_interview = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider])
)-> InterviewFeedbackService:
    return InterviewFeedbackService(validator , gemini_service , repo_interview)

@inject
def get_interview_score_service(
    validator = Depends(Provide[ApplicationContainer.service.validator_service]),
    repo_interview = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider])
)-> InterviewScoreService:
    return InterviewScoreService(validator , repo_interview)