from backend.core.job_triggers.text_job_trigger_service import TextJobTriggerService
from backend.core.job_triggers.video_job_trigger_service import VideoJobTriggerService
from backend.core.job_triggers.email_job_trigger_service import  EmailJobTriggerService
def get_video_job_trigger_service() -> VideoJobTriggerService:
    return VideoJobTriggerService()

def get_text_job_trigger_service() -> TextJobTriggerService:
    return TextJobTriggerService()

def get_email_job_trigger_service() -> EmailJobTriggerService:
    return EmailJobTriggerService()