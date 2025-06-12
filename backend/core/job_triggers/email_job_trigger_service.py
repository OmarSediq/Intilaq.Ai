from rq import Queue
from redis import Redis
from backend.core.job_runners.send_invitation_job import send_invitation_job

class EmailJobTriggerService:
    def __init__(self):
        self.redis_conn = Redis.from_url("redis://redis-container:6379")
        self.queue = Queue(name="default", connection=self.redis_conn)

    def trigger_send_invitation_job(self, emails, job_title, raw_date, interview_link, hr_id):
        self.queue.enqueue(
            send_invitation_job,
            emails,
            job_title,
            raw_date,
            interview_link,
            hr_id
        )
