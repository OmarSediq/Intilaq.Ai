# from datetime import datetime, timezone , timedelta
# from backend.core.base_service import TraceableService
# from backend.core.job_dispatchers.text_dispatcher import TextDispatcherService
# from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
# from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
# from backend.data_access.mongo.hr.hr_invitation_repository import HRInvitationRepository
# from backend.data_access.mongo.hr.hr_interview_gridfs_repository import HRGridFSStorageService
# from typing import Optional
# from fastapi import UploadFile
# from backend.core.job_dispatchers.video_dispatcher import VideoDispatcherService
# from backend.domain_services.video.video_metadata_service import VideoMetadataService
# import uuid
# from backend.data_access.mongo.task.tasks_repository import TasksRepository
# # from backend.core.providers.infra_providers import get_mongo_db


# class HRAnswerService(TraceableService):
#     def __init__(
#         self,
#         answer_repo: HRAnswerRepository,
#         invitation_repo: HRInvitationRepository,
#         gridfs_storage: HRGridFSStorageService,
#         video_job_dispatcher: VideoDispatcherService,
#         text_job_dispatcher : TextDispatcherService ,
#         question_repo : HRInterviewRepository ,
#         tasks_repo : TasksRepository

#     ):
#         self.repo = answer_repo
#         self.invitation_repo = invitation_repo
#         self.gridfs_storage = gridfs_storage
#         self.video_job_dispatcher = video_job_dispatcher
#         self.text_job_dispatcher = text_job_dispatcher
#         self.question_repo = question_repo
#         self.tasks_repo = tasks_repo

#     async def create_session(self, interview_token: str, name: str, email: str):
#         interview = await self.invitation_repo.get_interview_by_token(interview_token)
#         if not interview:
#             raise ValueError("Invalid interview token")

#         if await self.repo.session_exists_for_create(interview_token , email):
#             raise ValueError("Session already started for this email")

#         now = datetime.utcnow()
#         hr_id = interview.get("hr_id")
#         await self.repo.create_session(interview_token, name, email, now, hr_id=hr_id)
#         return now

#     async def upload_answer(
#             self,
#             interview_token: str,
#             index: int,
#             user_email: str,
#             file: UploadFile = None,
#             text_answer: Optional[str] = None
#         ):

#         session = await self.repo.get_session_by_token_and_email(interview_token, user_email)
#         if not session:
#             raise ValueError("Session not found for this user")

#         now = datetime.now(timezone.utc)
#         start_time = now
#         end_time = now
#         answer_duration = None
#         time_exceeded = False
#         response_type = "text"
#         video_file_id = None

#         question = await self.question_repo.get_question_by_index(interview_token, index)
#         time_limit = question.get("time_limit")

#         if file is not None and file.filename.strip():
#             filename = f"{interview_token}_q{index}_{file.filename}"
#             video_bytes = await file.read()

#             metadata_service = VideoMetadataService()
#             duration = metadata_service.get_duration(video_bytes)

#             if duration > 0:
#                 answer_duration = round(duration)
#                 end_time = now
#                 start_time = end_time - timedelta(seconds=answer_duration)

#                 if time_limit and answer_duration > time_limit:
#                     time_exceeded = True

#             file.file.seek(0)
#             video_file_id = await self.gridfs_storage.upload_video(filename, file.file)
#             response_type = "video"
#             text_answer = None

#         elif text_answer:
#             word_count = len(text_answer.strip().split())
#             approx_duration = round((word_count / 30) * 60)
#             end_time = now
#             start_time = now - timedelta(seconds=approx_duration)
#             answer_duration = approx_duration

#             if time_limit and approx_duration > time_limit:
#                 time_exceeded = True

#         answer_doc = {
#             "question_index": index,
#             "start_time": start_time,
#             "end_time": end_time,
#             "answer_duration": answer_duration,
#             "question_time_limit": time_limit,
#             "time_exceeded": time_exceeded,
#             "response_type": response_type,
#             "video_file_id": video_file_id,
#             "answer_text": text_answer,
#         }

#         await self.repo.add_answer_to_user(interview_token, user_email, answer_doc)

#         if response_type == "video":
#             job_id = uuid.uuid4().hex
#             payload_ref = video_file_id
#             task_doc = {
#                 "_id": job_id,
#                 "type": "video_processing",
#                 "status": "pending",
#                 "payload_ref": payload_ref,
#                 "attempts": 0,
#                 "max_attempts": int(__import__("os").environ.get("TASK_MAX_ATTEMPTS", "5")),
#                 "idempotency_key": video_file_id,
#                 "created_at": datetime.utcnow(),
#                 "updated_at": datetime.utcnow(),
#             }

            
#             await self.tasks_repo.insert_task(task_doc)

#             try:
#                 await self.video_job_dispatcher.dispatch_video_processing(video_file_id,interview_token,user_email,index)

#                 await self.tasks_repo.col.update_one(
#                     {"_id": job_id},
#                     {"$set": {"status": "queued", "queued_at": datetime.utcnow(), "updated_at": datetime.utcnow()}}
#                 )
#             except Exception as exc:
#                 await self.tasks_repo.mark_failed(job_id, reason=f"enqueue_failed:{str(exc)}")
#                 raise

#             return {"job_id": job_id, "answer": await self.repo.get_answer_by_index(interview_token, user_email, index)}
#         else:
#             await self.text_job_dispatcher.dispatch_text_evaluation(interview_token, user_email, index)
#             return await self.repo.get_answer_by_index(interview_token, user_email, index)
