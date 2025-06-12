from datetime import datetime, timezone , timedelta
from backend.core.base_service import TraceableService
from backend.core.job_triggers.text_job_trigger_service import TextJobTriggerService
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from backend.data_access.mongo.hr.hr_invitation_repository import HRInvitationRepository
from backend.data_access.mongo.hr.hr_interview_gridfs_repository import HRGridFSStorageService
from typing import Optional
from fastapi import UploadFile
from backend.core.job_triggers.video_job_trigger_service import VideoJobTriggerService
from backend.domain_services.video.video_metadata_service import VideoMetadataService


class HRAnswerService(TraceableService):
    def __init__(
        self,
        answer_repo: HRAnswerRepository,
        invitation_repo: HRInvitationRepository,
        gridfs_storage: HRGridFSStorageService,
        video_job_trigger: VideoJobTriggerService,
        text_job_trigger : TextJobTriggerService ,
        question_repo : HRInterviewRepository
    ):
        self.repo = answer_repo
        self.invitation_repo = invitation_repo
        self.gridfs_storage = gridfs_storage
        self.video_job_trigger = video_job_trigger
        self.text_job_trigger = text_job_trigger
        self.question_repo = question_repo

    async def create_session(self, interview_token: str, name: str, email: str):
        interview = await self.invitation_repo.get_interview_by_token(interview_token)
        if not interview:
            raise ValueError("Invalid interview token")

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
        exists = await self.repo.session_exists(interview_token)
        if not exists:
            raise ValueError("Session not found")

        now = datetime.now(timezone.utc)
        start_time = now
        end_time = now
        answer_duration = None
        time_exceeded = False
        response_type = "text"
        video_file_id = None


        question = await self.question_repo.get_question_by_index(interview_token, index)
        time_limit = question.get("time_limit")  # may be None


        if file is not None and file.filename:
            filename = f"{interview_token}_q{index}_{file.filename}"
            video_bytes = await file.read()

            metadata_service = VideoMetadataService()
            duration = metadata_service.get_duration(video_bytes)

            if duration > 0:
                answer_duration = round(duration)
                end_time = now
                start_time = end_time - timedelta(seconds=answer_duration)

                if time_limit and answer_duration > time_limit:
                    time_exceeded = True

            file.file.seek(0)
            video_file_id = await self.gridfs_storage.upload_video(filename, file.file)
            response_type = "video"
            text_answer = None


        elif text_answer:
            word_count = len(text_answer.strip().split())
            approx_duration = round((word_count / 30) * 60)  # 40 word/minute = 1.5 second/word
            end_time = now
            start_time = now - timedelta(seconds=approx_duration)

            answer_duration = approx_duration
            if time_limit and approx_duration > time_limit:
                time_exceeded = True


        answer_doc = {
            "question_index": index,
            "start_time": start_time,
            "end_time": end_time,
            "answer_duration": answer_duration,
            "question_time_limit": time_limit,
            "time_exceeded": time_exceeded,
            "response_type": response_type,
            "video_file_id": video_file_id,
            "answer_text": text_answer,
        }

        await self.repo.add_answer(interview_token, answer_doc)

        if response_type == "video":
            self.video_job_trigger.trigger_video_processing(str(video_file_id))
        else:
            self.text_job_trigger.trigger_text_evaluation(interview_token, index)

        return await self.repo.get_answer_by_index(interview_token, index)

    async def get_video_bytes(self, file_id: str) -> bytes:
        try:
            return await self.gridfs_storage.get_video_by_file_id(file_id)
        except Exception as e:
            raise RuntimeError(f"Error fetching video from storage: {str(e)}")

