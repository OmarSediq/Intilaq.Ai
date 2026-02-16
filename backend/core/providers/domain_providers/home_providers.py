from fastapi import Depends
from backend.core.containers.application_container import ApplicationContainer
from backend.domain_services.home_services.interview_session_service import InterviewSessionHomeService  , InterviewSessionHomeRepository 
# from backend.core.providers.data_access_providers.home_providers.resume_download_repository_provider import get_resume_download_repository
from backend.domain_services.home_services.home_stats_service import HomeStatsRepository
# from backend.domain_services.home_services.resume_download_service import ResumeDownloadRepository , ResumeDownloadService
from dependency_injector.wiring import inject , Provide


@inject
def get_home_stats_service(
    repository = Depends(Provide[ApplicationContainer.repos.home_stats_repository_factory.provider])
)-> HomeStatsRepository: 
    return HomeStatsRepository(repository=repository)

@inject
def get_interview_session_service_home(
    mongo_repo = Depends(Provide[ApplicationContainer.repos.interview_session_home_repository_factory.provider]),
    redis_repo = Depends(Provide[ApplicationContainer.repos.session_redis_repository_factory.provider]),
    validator = Depends(Provide[ApplicationContainer.service.validator_service])
)-> InterviewSessionHomeService:
    return InterviewSessionHomeRepository(
        repository = mongo_repo,
        redis_repo=redis_repo,
        validator=validator
    )


# archive this next time (because i need to add all of generate (PDF,DOCS,HTML) to microservice)

# def get_resume_download_service(
#     repo: ResumeDownloadRepository = Depends(get_resume_download_repository)
# ) -> ResumeDownloadService:
#     return ResumeDownloadService(repository=repo)
