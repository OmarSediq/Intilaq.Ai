
from pydantic import BaseModel ,EmailStr 
from typing import Optional , Literal , List
from datetime import datetime



class InterviewMetadataRequest(BaseModel):
    job_title: str
    level: str
    job_requirements: Optional[str] = None
    time: Optional[str] = None
    date_range: Optional[str] = None  # could be a string like "2025-05-10 to 2025-05-12"


class HRAddQuestionRequest(BaseModel):
    question_text: Optional[str] = None
    response_type: Optional[Literal["text", "video"]] = None
    time_limit: Optional[int] = None


class InterviewInvitationRequest(BaseModel):
    emails: Optional[List[EmailStr]] = None
    email_description: Optional[str] = None
    interview_link:  Optional[str] = None