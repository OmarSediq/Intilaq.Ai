from fastapi import APIRouter, Depends
from app.api.auth_api.auth.routes_auth import get_current_user
from app.services.mongo_services import get_db  
from app.services.hr_services.hr_interview_services import create_hr_interview_metadata , update_interview_question_by_index , send_and_save_invitations
from app.schemas.hr_schemas.create_hr_interview import InterviewMetadataRequest  , HRAddQuestionRequest , InterviewInvitationRequest
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db  as db_post

router = APIRouter()

@router.post("/api/hr/interviews/create", tags=["HR - Create Interview Metadata"])
async def create_interview_metadata(
    request: InterviewMetadataRequest,
    user=Depends(get_current_user),
    db=Depends(get_db) 
):
    return await create_hr_interview_metadata(request, user["user_id"])


@router.put("/api/hr/interviews/{interview_token}/questions/{index}", tags=["HR - Interview Questions"])
async def update_interview_question(
    interview_token: str,
    index: int,
    request: HRAddQuestionRequest,
    user=Depends(get_current_user)
):
    return await update_interview_question_by_index(interview_token, index, request)



@router.post("/api/hr/interviews/{interview_token}/invitations/send", tags=["HR - Interview Invitations"])
async def send_and_store_invitations(
    interview_token: str,
    request: InterviewInvitationRequest,
    db: AsyncSession = Depends(db_post),
    user=Depends(get_current_user)
):
    return await send_and_save_invitations(
        interview_token=interview_token,
        emails=request.emails or [],
        email_description=request.email_description,
        interview_link=request.interview_link,
        db=db
    )

