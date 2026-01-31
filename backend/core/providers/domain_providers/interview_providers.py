from fastapi import Depends
from backend.domain_services.interview_services.session_service import InterviewSessionService
from backend.domain_services.interview_services.question_service import InterviewQuestionService
from backend.domain_services.interview_services.answer_service import InterviewAnswerService
from backend.domain_services.interview_services.feedback_service import InterviewFeedbackService
from backend.domain_services.interview_services.score_service import InterviewScoreService
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.containers.ai_container import AIContainer
from backend.core.containers.services_container import ServicesContainer
from dependency_injector.wiring import inject , Provide 


def get_validator_service(
    repo_interview = Depends(Provide[RepositoriesContainer.interview_repository_factory]),
    repo_session = Provide[RepositoriesContainer.session_redis_repository_factory]
)-> InterviewValidatorService: 
    return InterviewValidatorService(repo_interview , repo_session)



def get_interview_session_service(
    validator = Depends(Provide[ServicesContainer.validator_service]),
    gemini_service = Depends(Provide[AIContainer.gemini_service]),
    repo_interview = Depends(Provide[RepositoriesContainer.interview_repository_factory]),
    repo_session = Depends(Provide[RepositoriesContainer.session_redis_repository_factory])
)-> InterviewSessionService:
    return InterviewSessionService(validator , gemini_service , repo_interview , repo_session)

def get_interview_question_service(
    validator = Depends(Provide[ServicesContainer.validator_service]),
    repo_interview = Depends(Provide[RepositoriesContainer.interview_repository_factory]),
    repo_session = Depends(Provide[RepositoriesContainer.session_redis_repository_factory])
)-> InterviewQuestionService:
    return InterviewQuestionService(validator, repo_interview , repo_session)



def get_interview_answer_service(
    validator =Depends( Provide[ServicesContainer.validator_service]),
    whisper_service = Depends(Provide[AIContainer.whisper_transcriber]),
    repo_interview = Depends(Provide[RepositoriesContainer.interview_repository_factory]),
    repo_session = Depends(Provide[RepositoriesContainer.session_redis_repository_factory])
)-> InterviewAnswerService:
    return InterviewAnswerService(validator , repo_interview , repo_session , whisper_service)


def get_interview_feedback_service(
    validator = Depends(Provide[ServicesContainer.validator_service]),
    gemini_service = Depends(Provide[AIContainer.gemini_service]),
    repo_interview = Depends(Provide[RepositoriesContainer.interview_repository_factory])
)-> InterviewFeedbackService:
    return InterviewFeedbackService(validator , gemini_service , repo_interview)


def get_interview_score_service(
    validator = Depends(Provide[ServicesContainer.validator_service]),
    repo_interview = Depends(Provide[RepositoriesContainer.interview_repository_factory])
)-> InterviewScoreService:
    return InterviewScoreService(validator , repo_interview)