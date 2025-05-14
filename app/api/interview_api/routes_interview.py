from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas.interview import JobData
from app.core.providers.services.user_provider import get_current_user
from app.services.interview_services.session_service import InterviewSessionService
from app.services.interview_services.question_service import InterviewQuestionService
from app.services.interview_services.answer_service import InterviewAnswerService
from app.services.interview_services.feedback_service import InterviewFeedbackService
from app.services.interview_services.score_service import InterviewScoreService
from app.core.providers.services.interview_providers import (
    get_interview_session_service,
    get_interview_question_service,
    get_interview_answer_service,
    get_interview_feedback_service,
    get_interview_score_service
    
)
from app.services.mongo_services import get_db

router = APIRouter()
@router.post("/api/sessions/", tags=["Interview Sessions"])
async def create_session(
    job_data: JobData,
    user=Depends(get_current_user),
    session_service: InterviewSessionService = Depends(get_interview_session_service)
):
    return await session_service.create_session(job_data, user)

@router.post("/api/sessions/{session_id}/start", tags=["Interview Sessions"])
async def start_session(
    session_id: int,
    user=Depends(get_current_user),
    session_service: InterviewSessionService = Depends(get_interview_session_service)
):
    return await session_service.start_session(session_id, user["user_id"])

@router.get("/api/sessions/{session_id}/questions", tags=["Interview Questions"])
async def get_questions(
    session_id: int,
    user=Depends(get_current_user),
    question_service: InterviewQuestionService = Depends(get_interview_question_service)
):
    return await question_service.get_questions(session_id, user["user_id"])

@router.get("/api/sessions/{session_id}/questions/next", tags=["Interview Questions"])
async def get_next_question(
    session_id: int,
    user=Depends(get_current_user),
    question_service: InterviewQuestionService = Depends(get_interview_question_service)
):
    return await question_service.get_next_question(session_id, user["user_id"])

@router.post("/api/sessions/{session_id}/answers", tags=["Answer Submission"])
async def submit_answer(
    session_id: int,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    answer_service: InterviewAnswerService = Depends(get_interview_answer_service)
):
    return await answer_service.submit_answer(session_id, file, user["user_id"])

@router.get("/api/sessions/{session_id}/answers/{question_index}/feedback", tags=["Answer Submission"])
async def get_feedback(
    session_id: int,
    question_index: int,
    user=Depends(get_current_user),
    feedback_service: InterviewFeedbackService = Depends(get_interview_feedback_service)
):
    return await feedback_service.get_feedback(session_id, question_index, user["user_id"])

@router.post("/api/sessions/{session_id}/end", tags=["Interview Sessions"])
async def end_session(
    session_id: int,
    user=Depends(get_current_user),
    db=Depends(get_db),
    score_service: InterviewScoreService = Depends(get_interview_score_service)
):
    return await score_service.end_session(session_id, user["user_id"], db)

@router.get("/api/sessions/{session_id}/score", tags=["Scoring"])
async def calculate_score(
    session_id: int,
    user=Depends(get_current_user),
    score_service: InterviewScoreService = Depends(get_interview_score_service)
):
    return await score_service.calculate_score(session_id, user["user_id"])
