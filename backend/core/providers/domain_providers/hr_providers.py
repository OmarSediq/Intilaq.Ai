# from backend.domain_services.hr_services.client_interview_services.hr_answer_service import HRAnswerService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.domain_services.hr_services.auth_services.hr_auth_service import HRAuthService
from backend.domain_services.hr_services.auth_services.hr_register_service import HRRegisterService
from backend.domain_services.hr_services.auth_services.hr_verification_service import HRVerificationService
from backend.domain_services.hr_services.create_interview_services.hr_interview_service import HRInterviewService
# from backend.domain_services.hr_services.create_interview_services.hr_invitation_service import HRInvitationService
from backend.domain_services.hr_services.home.hr_interview_evaluation_service import HRInterviewEvaluationService
from backend.core.containers.repositories_container import RepositoriesContainer
# from backend.core.containers.dispatchers_container import DispatchersContainer
from backend.core.containers.ai_container import AIContainer
from backend.core.containers.services_container import ServicesContainer
from backend.core.dependencies.session.postgres import provide_request_postgres_session
# from backend.core.providers.queue_provider import  get_text_job_dispatcher_service , get_video_job_dispatcher_service
from dependency_injector.wiring import inject , Provide
from motor.motor_asyncio import   AsyncIOMotorGridFSBucket
from backend.core.dependencies.session.mongo import provide_hr_video_bucket


def get_hr_auth_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    hr_repo =Depends(Provide[RepositoriesContainer.hr_auth_repository_factory]),
    token_service = Depends(Provide[ServicesContainer.token_service])
)->HRAuthService:
    return HRAuthService(db=db , hr_repo=hr_repo , token_service=token_service)



def get_hr_register_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    hr_repo = Depends(Provide[RepositoriesContainer.hr_auth_repository_factory])
)-> HRRegisterService:
    return HRRegisterService(db=db , hr_repo=hr_repo)



def get_hr_verification_service(
    db: AsyncSession= Depends(provide_request_postgres_session),
    hr_repo = Depends(Provide[RepositoriesContainer.hr_auth_repository_factory])
)-> HRVerificationService:
    return HRVerificationService(db = db , hr_repo = hr_repo)


def get_hr_interview_service(
    repository = Depends(Provide[RepositoriesContainer.hr_interview_repository_factory]),
    gemini_service=Depends(Provide[AIContainer.gemini_service])
)-> HRInterviewService:
    return HRInterviewService(repository=repository , gemini_service=gemini_service)



# def get_hr_invitation_service(
#     db : AsyncSession= Depends(provide_request_postgres_session),
#     repo = Depends(Provide[RepositoriesContainer.hr_invitation_repository_factory]),
#     email_dispatcher =Depends( Provide[DispatchersContainer.email_dispatcher])
# )-> HRInvitationService:
#     return HRInvitationService(repo = repo , db=db , email_dispatcher=email_dispatcher)





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



def get_hr_interview_evaluation_service(
    repo = Depends(Provide[RepositoriesContainer.hr_interview_evaluation_repository_factory]),
    bucket : AsyncIOMotorGridFSBucket = Depends(provide_hr_video_bucket),
    question_repo = Depends(Provide[RepositoriesContainer.hr_interview_repository_factory])

)-> HRInterviewEvaluationService:
    return HRInterviewEvaluationService(evaluation_repo=repo , bucket=bucket , question_repo=question_repo)




