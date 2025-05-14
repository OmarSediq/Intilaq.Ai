
from fastapi import Depends

from app.services.mongo_services import get_mongo_client


from app.services.home_services.home_stats_service import HomeStatsService
from app.services.home_services.interview_session_service import InterviewSessionServiceHome
from app.services.home_services.resume_download_service import ResumeDownloadService
from app.services.interview_services.validator_service import InterviewValidatorService

# ========== Home ==========

validator_instance = InterviewValidatorService() 

def get_home_stats_service(mongo_client=Depends(get_mongo_client)):
    return HomeStatsService(mongo_client )

def get_interview_session_service_home(mongo_client=Depends(get_mongo_client)):
    return InterviewSessionServiceHome(mongo_client , validator_instance)

def get_resume_download_service(mongo_client=Depends(get_mongo_client)):
    return ResumeDownloadService(mongo_client)
