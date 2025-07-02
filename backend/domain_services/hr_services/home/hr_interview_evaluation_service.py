from typing import Optional
from bson import ObjectId
from backend.core.base_service import TraceableService
from backend.data_access.mongo.hr.hr_interview_evaluation_repository import HRInterviewEvaluationRepository
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
class HRInterviewEvaluationService(TraceableService):
    def __init__(self, evaluation_repo: HRInterviewEvaluationRepository, bucket: AsyncIOMotorGridFSBucket ,question_repo : HRInterviewRepository ):
        self.repo = evaluation_repo
        self.bucket = bucket
        self.question_repo = question_repo

    async def get_video_stream_by_index(self, interview_token: str, user_email: str, index: int):
        file_doc = await self.repo.get_video_file_by_token_and_index(interview_token, user_email, index)
        if not file_doc:
            return None, None

        file_id = file_doc["video_file_id"]
        file_stream = await self.bucket.open_download_stream(ObjectId(file_id))
        filename = f"{interview_token}_q{index}_output.webm"
        return file_stream, filename

    async def get_answer_indexes_by_type(self, interview_token: str, user_email: str) -> dict:
        result = await self.repo.get_answer_type_indexes(interview_token, user_email)
        result.pop("_id", None)
        return result


    async def get_video_question_details(self, interview_token: str, user_email: str, index: int):

        video_answer = await self.repo.get_video_file_by_token_and_index(interview_token, user_email, index)
        if not video_answer:
            return None
        question_data = await self.question_repo.get_question_by_token_and_index(interview_token, index)
        return question_data

    async def get_text_question_and_answer(
            self, interview_token: str, index: int, user_email: str
    ) -> Optional[dict]:
        return await self.question_repo.get_text_question_and_user_answer(
            interview_token, index, user_email
        )
