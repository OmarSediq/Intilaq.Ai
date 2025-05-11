
from pydantic import BaseModel ,EmailStr 
from typing import Optional , Literal , List
from datetime import datetime



class InterviewMetadataRequest(BaseModel):
    job_title: str
    level: str
    job_requirements: Optional[str] = None
    specific_date: Optional[datetime] = None
    time: Optional[str] = None
    date_range: Optional[str] = None  # could be a string like "2025-05-10 to 2025-05-12"


class HRAddQuestionRequest(BaseModel):
    question_text: str
    response_type: Literal["text", "video"]
    time_limit: Optional[int] = None



class InterviewInvitationRequest(BaseModel):
    emails: Optional[List[EmailStr]] = None
    email_description: Optional[str] = None
    interview_link: str