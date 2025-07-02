from pydantic import BaseModel, EmailStr
from typing import Optional

class InterviewLoginRequest(BaseModel):
    name: str
    email: EmailStr

class InterviewAnswerRequest(BaseModel):
    text_answer: Optional[str] = None
