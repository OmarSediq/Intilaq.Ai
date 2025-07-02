from fastapi import APIRouter, Depends
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.schemas.hr_schemas.hr_create_schema import (
    InterviewMetadataRequest,
    HRAddQuestionRequest,
    InterviewInvitationRequest
)
from backend.domain_services.hr_services.create_interview_services.hr_interview_service import HRInterviewService
from backend.domain_services.hr_services.create_interview_services.hr_invitation_service import HRInvitationService
from backend.core.providers.domain_providers.hr_providers import get_hr_interview_service, get_hr_invitation_service
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.core.providers.domain_providers.hr_providers import get_hr_interview_evaluation_service
from backend.domain_services.hr_services.home.hr_interview_evaluation_service import HRInterviewEvaluationService
from backend.utils.response_schemas import success_response, error_response
from backend.core.providers.domain_providers.hr_summary_service_provider import get_hr_summary_service
from backend.domain_services.hr_services.hr_summary_service import HRUserSummaryService

router = APIRouter()

@router.post("/api/hr/interview/create", tags=["HR - Interview"])
async def create_interview_metadata(
    request: InterviewMetadataRequest,
    user=Depends(get_current_user),
    service: HRInterviewService = Depends(get_hr_interview_service)
):
    return await service.create_metadata(request, hr_id=user["user_id"])


@router.put("/api/hr/interview/{interview_token}/questions/{index}", tags=["HR - Interview"])
async def update_interview_question(
    interview_token: str,
    index: int,
    request: HRAddQuestionRequest,
    user=Depends(get_current_user),
    service: HRInterviewService = Depends(get_hr_interview_service)
):
    return await service.update_question(interview_token, index, request)


@router.post("/api/hr/interview/{interview_token}/invitations/send",tags=["HR - Interview"])
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

from fastapi import Query

@router.get("/api/hr/interview/video-stream/{interview_token}/{index}" ,  tags=["HR - Review"])
async def stream_video_by_index(
    interview_token: str,
    index: int,
    user_email: str = Query(...),

    evaluation_service: HRInterviewEvaluationService = Depends(get_hr_interview_evaluation_service)
):
    file_stream, filename = await evaluation_service.get_video_stream_by_index(interview_token, user_email, index)
    if not file_stream:
        raise HTTPException(status_code=404, detail="Video not found for the given index")

    return StreamingResponse(
        file_stream,
        media_type="video/webm",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Accept-Ranges": "bytes"
        }
    )


@router.get("/api/hr/interview/answer/{interview_token}/{index}", tags=["HR - Review"])
async def get_unified_answer_by_index(
    interview_token: str,
    index: int,
    user_email: str = Query(...),
    service: HRInterviewService = Depends(get_hr_interview_service),

):
    return await service.get_unified_answer_by_index(
        interview_token=interview_token,
        user_email=user_email,
        index=index
    )

@router.put("/api/hr/interview/{interview_token}/review-status" , tags=["HR - Review"])
async def update_review_status(
    interview_token: str,
    user_email: str =  Query(...),
    status: str =  Query(...),
    service: HRUserSummaryService = Depends(get_hr_summary_service)
):
    try:
        result = await service.update_review_status(interview_token, user_email, status)
        return success_response(code=200, data=result, message="Review status updated")
    except ValueError as ve:
        return error_response(code=400, error_message=str(ve))


@router.get("/api/hr/dashboard" , tags=["HR - Dashboard"])
async def hr_dashboard(
    current_user = Depends(get_current_user),
    summary_service: HRUserSummaryService = Depends(get_hr_summary_service)
):

    hr_id = current_user["user_id"]
    data = await summary_service.get_dashboard(hr_id=hr_id)
    return success_response(code=200, data=data)

@router.get("/api/hr/interview/{interview_token}/participants" , tags=["HR - Dashboard"])
async def get_participants(
    interview_token: str,
    user: dict = Depends(get_current_user),
    service: HRUserSummaryService = Depends(get_hr_summary_service)
):
    try:
        hr_id = user["user_id"]
        result = await service.get_interview_participants(interview_token, hr_id)
        return success_response(code=200, data=result)
    except ValueError as e:
        return error_response(code=404, error_message=str(e))


@router.get("/api/hr/questions/basic/{interview_token}/", tags=["HR - Interview"])
async def get_all_basic_questions_route(
    interview_token: str,
    service: HRInterviewService = Depends(get_hr_interview_service)
):
    return await service.get_all_basic_questions(interview_token)
