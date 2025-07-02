import os
from rq import Worker, Queue
from redis import Redis

listen = ['default']
redis_url = os.getenv("REDIS_URL", "redis://redis-container:6379")
conn = Redis.from_url(redis_url)

if __name__ == '__main__':
    worker = Worker(
        queues=listen,
        connection=conn,
        default_result_ttl=600,
        default_worker_ttl=600
    )
    worker.work()
