from fastapi import APIRouter, Depends
from app.core.providers.domain_providers.user_provider import get_current_user
from app.schemas.hr_schemas.create_hr_interview import (
    InterviewMetadataRequest,
    HRAddQuestionRequest,
    InterviewInvitationRequest
)
from app.domain_services.hr_services.create_interview_services.hr_interview_service import HRInterviewService
from app.domain_services.hr_services.create_interview_services.hr_invitation_service import HRInvitationService
from app.core.providers.domain_providers.hr_providers import get_hr_interview_service, get_hr_invitation_service

router = APIRouter()

@router.post("/api/hr/interviews/create", tags=["HR - Create Interview Metadata"])
async def create_interview_metadata(
    request: InterviewMetadataRequest,
    user=Depends(get_current_user),
    service: HRInterviewService = Depends(get_hr_interview_service)
):
    return await service.create_metadata(request, hr_id=user["user_id"])


@router.put("/api/hr/interviews/{interview_token}/questions/{index}", tags=["HR - Interview Questions"])
async def update_interview_question(
    interview_token: str,
    index: int,
    request: HRAddQuestionRequest,
    user=Depends(get_current_user),
    service: HRInterviewService = Depends(get_hr_interview_service)
):
    return await service.update_question(interview_token, index, request)


@router.post("/api/hr/interviews/{interview_token}/invitations/send", tags=["HR - Interview Invitations"])
async def send_and_store_invitations(
    interview_token: str,
    request: InterviewInvitationRequest,
    user=Depends(get_current_user),
    service: HRInvitationService = Depends(get_hr_invitation_service)
):
    return await service.send_invitations(
        interview_token=interview_token,
        emails=request.emails or [],
        email_description=request.email_description,
        interview_link=request.interview_link
    )
