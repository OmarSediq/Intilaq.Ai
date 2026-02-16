from fastapi import Depends
from backend.core.containers.application_container import ApplicationContainer
from backend.domain_services.hr_services.hr_summary_service import HRUserSummaryService
from dependency_injector.wiring import inject , Provide 

@inject
def get_hr_summary_service(
    answer_repo_factory = Depends(Provide[ApplicationContainer.repos.hr_interview_client_repository_factory.provider]),
    interview_repo_factory = Depends(Provide[ApplicationContainer.repos.hr_interview_repository_factory.provider]),
    summary_repo_factory = Depends(Provide[ApplicationContainer.repos.hr_summary_repository_factory.provider] )
)->HRUserSummaryService:
    answer_repo = answer_repo_factory()
    interview_repo = interview_repo_factory()
    summary_repo = summary_repo_factory()

    return HRUserSummaryService(answer_repo=answer_repo , interview_repo=interview_repo , summary_repo=summary_repo)