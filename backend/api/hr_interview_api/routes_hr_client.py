from backend.domain_services.hr_services.client_interview_services.hr_answer_service import HRAnswerService
from backend.core.providers.domain_providers.hr_providers import get_hr_answer_service
from backend.utils.response_schemas import success_response, error_response
from fastapi import APIRouter, UploadFile, File, Form, Depends
from backend.schemas.hr_schemas.hr_client_schema import InterviewLoginRequest , InterviewAnswerRequest

router = APIRouter()
@router.post("/api/hr/interviews/login/{interview_token}")
async def login_to_interview(
    interview_token: str,
    user: InterviewLoginRequest,
    service: HRAnswerService = Depends(get_hr_answer_service)
):

    try:
        login_time = await service.create_session(interview_token, user.name, user.email)
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


@router.post("/api/hr/interviews/{interview_token}/question/{index}/answer")
async def submit_answer(
    interview_token: str,
    index: int,
    json_data: str = Form(...),
    file: UploadFile = File(None),
    service: HRAnswerService = Depends(get_hr_answer_service)
):
    try:
        parsed_data = InterviewAnswerRequest.parse_raw(json_data)

        result = await service.upload_answer(
            interview_token=interview_token,
            index=index,
            file=file,
            text_answer=parsed_data.text_answer
        )
        return success_response(code=200, data=result, message="Answer submitted")
    except ValueError as e:
        return error_response(code=400, error_message=str(e))
    except Exception as e:
        return error_response(code=500, error_message="Unexpected error", data={"details": str(e)})
