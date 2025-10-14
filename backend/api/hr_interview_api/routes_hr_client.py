from typing import Optional

from backend.domain_services.hr_services.client_interview_services.hr_answer_service import HRAnswerService
from backend.core.providers.domain_providers.hr_providers import get_hr_answer_service
from backend.utils.response_schemas import success_response, error_response
from fastapi import APIRouter, UploadFile, File, Form, Depends
from backend.schemas.hr_schemas.hr_client_schema import InterviewLoginRequest , InterviewAnswerRequest
# from backend.core.job_dispatchers.video_jobs import enqueue_process_video_job
from backend.core.providers.domain_providers.hr_summary_service_provider import (
    get_hr_summary_service,
)
from backend.domain_services.hr_services.hr_summary_service import HRUserSummaryService
from fastapi import Query

router = APIRouter()
@router.post("/api/hr/interview/login/{interview_token}" , tags=["HR - Interview"])
async def login_to_interview(
    interview_token: str,
    user: InterviewLoginRequest,
    service: HRAnswerService = Depends(get_hr_answer_service),
    summary_service: HRUserSummaryService = Depends(get_hr_summary_service)
):

    try:
        login_time = await service.create_session(interview_token, user.name, user.email)
        await summary_service.list_participants(interview_token)
        return success_response(
            code=200,
            data={
                "interview_token": interview_token,
                "login_time": login_time.isoformat()
            },
            message="Login successful"
        )
    except ValueError as e:
        return error_response(code=409, error_message=str(e))


@router.post("/api/hr/interview/{interview_token}/question/{index}/answer", tags=["HR - Interview"] )
async def submit_answer(
    interview_token: str,
    index: int,
    user_email: str = Form(...),
    json_data: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    service: HRAnswerService = Depends(get_hr_answer_service)
):
    try:

        if not file and not json_data:
            return error_response(code=400, error_message="Either a video file or text answer must be provided.")

        text_answer = None
        if json_data:
            parsed = InterviewAnswerRequest.parse_raw(json_data)
            text_answer = parsed.text_answer

        result = await service.upload_answer(
            interview_token=interview_token,
            index=index,
            user_email=user_email,
            file=file,
            text_answer=text_answer
        )

        return success_response(code=200, data=result, message="Answer submitted")

    except ValueError as e:
        return error_response(code=400, error_message=str(e))
    except Exception as e:
        return error_response(code=500, error_message="Unexpected error", data={"details": str(e)})



# @router.post("/upload" , tags=["HR - Interview"])
# async def upload_video_route(video_id: str):
#     enqueue_process_video_job(video_id)
#     return {"message": "Video processing started in background"}


@router.get("/api/hr/interview/{interview_token}/overall-score" , tags=["HR - Interview"])
async def get_overall_score_endpoint(
    interview_token: str,
    user_email: str = Query(...),
    service: HRUserSummaryService = Depends(get_hr_summary_service),
):
    try:
        overall = await service.get_overall_score(interview_token, user_email)
        return success_response(
            code=200,
            data={"overall_score": overall},
            message="Overall score calculated successfully.",
        )
    except ValueError as e:
        return error_response(code=404, error_message=str(e))


