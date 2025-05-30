from datetime import datetime, timezone
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.data_access.mongo.hr.hr_invitation_repository import HRInvitationRepository
from typing import Optional
from fastapi import UploadFile

class HRAnswerService:
    def __init__(self, answer_repo: HRAnswerRepository, invitation_repo: HRInvitationRepository):
        self.repo = answer_repo
        self.invitation_repo = invitation_repo

    async def create_session(self, interview_token: str, name: str, email: str):

        interview = await self.invitation_repo.get_interview_by_token(interview_token)
        if not interview:
            raise ValueError("Invalid interview token")

        # تحقق أنه لم يُستخدم سابقًا
        existing = await self.repo.get_session_by_token(interview_token)
        if existing:
            raise ValueError("Session already started")

        now = datetime.utcnow()
        await self.repo.create_session(interview_token, name, email, now)
        return now

    async def upload_answer(
            self,
            interview_token: str,
            index: int,
            file: UploadFile = None,
            text_answer: Optional[str] = None
    ):
        session = await self.repo.get_session_by_token(interview_token)
        if not session:
            raise ValueError("Session not found")

        now = datetime.now(timezone.utc)
        video_file_id = None
        response_type = "text"


        if file is not None and file.filename:
            filename = f"{interview_token}_q{index}_{file.filename}"
            video_file_id = await self.repo.upload_video(filename, file.file)
            response_type = "video"
            text_answer = None

        answer_doc = {
            "question_index": index,
            "start_time": now,
            "end_time": now,
            "response_type": response_type,
            "video_file_id": video_file_id,
            "answer_text": text_answer,
        }

        await self.repo.add_answer(interview_token, answer_doc)
        return answer_doc
