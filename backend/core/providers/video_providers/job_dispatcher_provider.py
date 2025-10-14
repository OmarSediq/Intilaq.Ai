from backend.core.job_dispatchers.text_dispatcher import TextDispatcherService
from backend.core.job_dispatchers.video_dispatcher import VideoDispatcherService
from backend.core.job_dispatchers.email_dispatcher import  EmailDispatcherService


async def get_video_job_dispatcher_service() -> VideoDispatcherService:
       return await VideoDispatcherService.create()

def get_text_job_dispatcher_service() -> TextDispatcherService:
    return TextDispatcherService()

def get_email_job_dispatcher_service() -> EmailDispatcherService:
    return EmailDispatcherService()