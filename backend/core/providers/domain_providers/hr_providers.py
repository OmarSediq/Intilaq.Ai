# from backend.domain_services.hr_services.client_interview_services.hr_answer_service import HRAnswerService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.containers.application_container import ApplicationContainer
from backend.domain_services.hr_services.auth_services.hr_auth_service import HRAuthService
from backend.domain_services.hr_services.auth_services.hr_register_service import HRRegisterService
from backend.domain_services.hr_services.auth_services.hr_verification_service import HRVerificationService
from backend.domain_services.hr_services.create_interview_services.hr_interview_service import HRInterviewService
from backend.domain_services.hr_services.create_interview_services.hr_invitation_service import HRInvitationService
from backend.domain_services.hr_services.home.hr_interview_evaluation_service import HRInterviewEvaluationService
# from backend.core.containers.dispatchers_container import DispatchersContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
# from backend.core.providers.queue_provider import  get_text_job_dispatcher_service , get_video_job_dispatcher_service
from dependency_injector.wiring import inject , Provide
from backend.domain_services.token_services.refresh_token_service import RefreshTokenService
from backend.domain_services.token_services.token_service import TokenService

@inject
async def get_hr_auth_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    hr_repo_factory =Depends(Provide[ApplicationContainer.repos.hr_auth_repository_factory.provider]),
    token_service: TokenService = Depends(Provide[ApplicationContainer.service.token_service]),
    refresh_token_service : RefreshTokenService= Depends(Provide[ApplicationContainer.service.refresh_token_service])
)->HRAuthService:
    hr_repo = hr_repo_factory(db)
   
    return HRAuthService(db=db , hr_repo=hr_repo , token_service=token_service , refresh_token_service=refresh_token_service)


@inject
def get_hr_register_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    hr_repo_factory = Depends(Provide[ApplicationContainer.repos.hr_auth_repository_factory.provider])
)-> HRRegisterService:
    hr_repo = hr_repo_factory(db)
    return HRRegisterService(db=db , hr_repo=hr_repo)


@inject
def get_hr_verification_service(
    db: AsyncSession= Depends(provide_request_postgres_session),
    hr_repo_factory = Depends(Provide[ApplicationContainer.repos.hr_auth_repository_factory.provider])
)-> HRVerificationService:
    hr_repo = hr_repo_factory(db)
    return HRVerificationService(db = db , hr_repo = hr_repo)

@inject 
def get_hr_interview_service(
    hr_repo_factory = Depends(Provide[ApplicationContainer.repos.hr_interview_repository_factory.provider]),
    gemini_service=Depends(Provide[ApplicationContainer.ai.gemini_service])
)-> HRInterviewService:
    hr_repo = hr_repo_factory()  

    return HRInterviewService(hr_repo=hr_repo , gemini_service=gemini_service)


@inject
def get_hr_invitation_service(
    db: AsyncSession = Depends(provide_request_postgres_session),
    repo = Depends(Provide[ApplicationContainer.repos.hr_invitation_repository_factory.provider]),
    hr_repo = Depends(Provide[ApplicationContainer.repos.hr_user_repository_factory.provider]),
    email_event_publisher =Depends( Provide[ApplicationContainer.messaging.email_event_publisher])
)-> HRInvitationService:
    hr_repo = hr_repo(db)
    repo = repo()
    return HRInvitationService(repo = repo , hr_repo=hr_repo , email_event_publisher=email_event_publisher)





# def get_hr_answer_service(
#     answer_repo = Depends(Provide[RepositoriesContainer.hr_interview_client_repository_factory]),
#     invitation_repo = Depends(Provide[RepositoriesContainer.hr_invitation_repository_factory]),
#     gridfs_storage = Depends(Provide[RepositoriesContainer.hr_gridfs_storage_repository_factory]),
#     video_job_dispatcher = Depends(get_video_job_dispatcher_service),
#     text_job_dispatcher = Depends(get_text_job_dispatcher_service),
#     question_repo = Depends(Provide[RepositoriesContainer.hr_interview_repository_factory]),
#     tasks_repo = Depends(Provide[RepositoriesContainer.tasks_repository_factory])
# )-> HRAnswerService:
#     return HRAnswerService(answer_repo=answer_repo , invitation_repo=invitation_repo , gridfs_storage=gridfs_storage , video_job_dispatcher=video_job_dispatcher, text_job_dispatcher=text_job_dispatcher , question_repo=question_repo , tasks_repo=tasks_repo)


@inject
def get_hr_interview_evaluation_service(
    repo = Depends(Provide[ApplicationContainer.repos.hr_interview_evaluation_repository_factory.provider]),
    question_repo = Depends(Provide[ApplicationContainer.repos.hr_interview_repository_factory.provider])
)-> HRInterviewEvaluationService:
    repo = repo()
    question_repo = question_repo()
    return HRInterviewEvaluationService(evaluation_repo=repo , question_repo=question_repo)




