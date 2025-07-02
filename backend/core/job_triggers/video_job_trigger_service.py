from rq import Queue
from redis import Redis
from backend.core.job_runners.process_video_pipeline_job import run as run_video_pipeline_job


class VideoJobTriggerService:
    def __init__(self):
        redis_conn = Redis(host="redis", port=6379, db=0)
        self.queue = Queue(name="default", connection=redis_conn , default_timeout=1200)

    def trigger_video_processing(self, video_id: str):
        self.queue.enqueue(run_video_pipeline_job, video_id)
        print(f"[JOB TRIGGER] Enqueued video job for video_id: {video_id}")
