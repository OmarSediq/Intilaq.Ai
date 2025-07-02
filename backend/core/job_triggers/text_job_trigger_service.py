from rq import Queue
from redis import Redis
from backend.core.job_runners.evaluate_transcription_job import run as run_text_evaluation_job


class TextJobTriggerService:
    def __init__(self):
        redis_conn = Redis(host="redis", port=6379, db=0)
        self.queue = Queue(name="default", connection=redis_conn , default_timeout=1200)

    def trigger_text_evaluation(self, interview_token: str, user_email: str, index: int):
        self.queue.enqueue(
            run_text_evaluation_job,
            interview_token, user_email, index
        )
        print(
            f"[JOB TRIGGER] Enqueued text evaluation job for interview_token: {interview_token}, user_email: {user_email}, index: {index}")
