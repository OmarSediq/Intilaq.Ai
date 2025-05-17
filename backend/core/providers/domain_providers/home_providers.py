from fastapi import Depends
from backend.domain_services.home_services.interview_session_service import InterviewSessionHomeService , SessionRedisRepository , InterviewSessionHomeRepository , InterviewValidatorService
from backend.core.providers.data_access_providers.home_providers.home_stats_repository_provider import get_home_stats_repository
from backend.core.providers.data_access_providers.home_providers.resume_download_repository_provider import get_resume_download_repository
from backend.core.providers.data_access_providers.home_providers.interview_session_home_repository_provider import get_interview_home_repository 
from backend.core.providers.data_access_providers.session_providers.session_redis_repository_provider import get_session_redis_repository
from backend.core.providers.domain_providers.interview_providers import get_validator_service
from backend.domain_services.home_services.home_stats_service import HomeStatsService , HomeStatsRepository
from backend.domain_services.home_services.resume_download_service import ResumeDownloadRepository , ResumeDownloadService
# ========== Home ==========

def get_home_stats_service(
    repo: HomeStatsRepository = Depends(get_home_stats_repository),
) -> HomeStatsService:
    return HomeStatsService(repository=repo)


def get_interview_session_service_home(
    mongo_repo: InterviewSessionHomeRepository = Depends(get_interview_home_repository),
    redis_repo: SessionRedisRepository = Depends(get_session_redis_repository),
    validator: InterviewValidatorService = Depends(get_validator_service)  
) -> InterviewSessionHomeService:
    return InterviewSessionHomeService(
        repository=mongo_repo,
        redis_repo=redis_repo,
        validator=validator
    )


def get_resume_download_service(
    repo: ResumeDownloadRepository = Depends(get_resume_download_repository)
) -> ResumeDownloadService:
    return ResumeDownloadService(repository=repo)
