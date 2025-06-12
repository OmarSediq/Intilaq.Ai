from redis import Redis
from rq import Queue
from backend.core.job_runners.process_video_pipeline_job import run

redis_url = "redis://redis-container:6379"
conn = Redis.from_url(redis_url)
queue = Queue("default", connection=conn , default_timeout=600)

def enqueue_process_video_job(video_id: str):
    queue.enqueue(run, video_id)
