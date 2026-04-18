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
    repo_interview_factory = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider]),
    repo_session_factory = Depends(Provide[ApplicationContainer.repos.session_redis_repository_factory.provider])
)-> InterviewValidatorService: 
    repo_interview = repo_interview_factory()
    repo_session = repo_session_factory()
    return InterviewValidatorService(repo_interview=repo_interview , repo_session =repo_session)


@inject
def get_interview_session_service(
    validator = Depends(Provide[ApplicationContainer.service.validator_service]),
    gemini_service = Depends(Provide[ApplicationContainer.ai.gemini_service]),
    repo_interview_factory  = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider]),
    repo_session_factory  = Depends(Provide[ApplicationContainer.repos.session_redis_repository_factory.provider])
)-> InterviewSessionService:
    repo_interview = repo_interview_factory()
    repo_session = repo_session_factory()
    return InterviewSessionService(validator=validator , gemini_service =gemini_service, repo_interview =repo_interview , repo_session=repo_session)

@inject
def get_interview_question_service(
    validator = Depends(Provide[ApplicationContainer.service.validator_service]),
    repo_interview_factory  = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider]),
    repo_session_factory = Depends(Provide[ApplicationContainer.repos.session_redis_repository_factory.provider])
)-> InterviewQuestionService:
    repo_interview = repo_interview_factory()
    repo_session = repo_session_factory()
    return InterviewQuestionService(validator=validator, repo_interview =repo_interview, repo_session=repo_session)


@inject
def get_interview_answer_service(
    validator =Depends( Provide[ApplicationContainer.service.validator_service]),
    whisper_service = Depends(Provide[ApplicationContainer.ai.whisper_transcriber]),
    repo_answer_factory = Depends(Provide[ApplicationContainer.repos.interview_answer_repository_factory.provider]),
    repo_session_factory = Depends(Provide[ApplicationContainer.repos.session_redis_repository_factory.provider])
)-> InterviewAnswerService:
    repo_answer = repo_answer_factory()
    repo_session = repo_session_factory()

    return InterviewAnswerService(validator =validator, repo_answer= repo_answer , repo_session=repo_session , whisper_service = whisper_service)

@inject
def get_interview_feedback_service(
    validator = Depends(Provide[ApplicationContainer.service.validator_service]),
    gemini_service = Depends(Provide[ApplicationContainer.ai.gemini_service]),
    repo_answer_factory  = Depends(Provide[ApplicationContainer.repos.interview_answer_repository_factory.provider])
)-> InterviewFeedbackService:
    repo_answer = repo_answer_factory()
    return InterviewFeedbackService(validator =validator, gemini_service =gemini_service, repo_answer =repo_answer)

@inject
def get_interview_score_service(
    validator = Depends(Provide[ApplicationContainer.service.validator_service]),
    repo_interview_factory  = Depends(Provide[ApplicationContainer.repos.interview_repository_factory.provider]),
    repo_answer_factory =  Depends(Provide[ApplicationContainer.repos.interview_answer_repository_factory.provider]),
    repo_session_result_factory =  Depends(Provide[ApplicationContainer.repos.interview_session_result_repository_factory.provider]),
    repo_user_home_summary_factory =  Depends(Provide[ApplicationContainer.repos.interview_home_summary_repository_factory.provider]),
)-> InterviewScoreService:
    repo_interview = repo_interview_factory()
    repo_answer = repo_answer_factory()
    repo_session_result = repo_session_result_factory()
    repo_user_home_summary = repo_user_home_summary_factory()
    return InterviewScoreService(validator=validator , repo_interview=repo_interview ,repo_answer = repo_answer , repo_session_result = repo_session_result  , repo_user_home_summary = repo_user_home_summary) 