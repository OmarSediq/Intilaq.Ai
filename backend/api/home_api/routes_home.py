from fastapi import APIRouter, Depends
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.domain_services.home_services.home_stats_service import HomeStatsService
from backend.domain_services.home_services.interview_session_service import InterviewSessionHomeService
from backend.domain_services.home_services.resume_download_service import ResumeDownloadService
from backend.core.providers.domain_providers.home_providers import (
    get_home_stats_service,
    get_interview_session_service_home,
    get_resume_download_service,
)

router = APIRouter()


@router.get("/api/home/summary", tags=["Home - Summary"])
async def get_home_summary(
    user=Depends(get_current_user),
    service: HomeStatsService = Depends(get_home_stats_service)
):
    return await service.get_summary(user["user_id"])


@router.get("/api/home/interview-sessions", tags=["Home - Summary"])
async def get_user_sessions(
    user=Depends(get_current_user),
    service: InterviewSessionHomeService = Depends(get_interview_session_service_home)
):
    return await service.get_sessions(user["user_id"])


@router.get("/api/sessions/{session_id}/details", tags=["Home - Summary"])
async def get_session_details(
    session_id: int,
    user=Depends(get_current_user),
    service: InterviewSessionHomeService = Depends(get_interview_session_service_home)
):
    return await service.get_session_details(session_id, user["user_id"])


@router.get("/api/resumes/download", tags=["Home - Summary"])
async def download_latest_resume(
    user=Depends(get_current_user),
    service: ResumeDownloadService = Depends(get_resume_download_service)
):
    return await service.download_latest_resume(user["user_id"])
