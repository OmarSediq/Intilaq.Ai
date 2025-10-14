import os
import signal
import sys
from redis import Redis
from rq import Worker
from backend.core.worker_service.loop_manager import LoopManager
from backend.core.providers.queue_provider import get_redis_conn  

loop_mgr = LoopManager()

def _graceful_shutdown(worker):
    try:
        worker.request_stop()
    except Exception:
        pass
    try:
        loop_mgr.stop()
    except Exception:
        pass

def main():
    loop_mgr.start()

    redis_conn = get_redis_conn()
    queues = os.getenv("QUEUES", "video").split(",")

    worker = Worker(queues, connection=redis_conn)

    # register OS signals to attempt graceful shutdown
    def _handle_sig(signum, frame):
        print(f"[worker] received signal {signum}, shutting down...")
        _graceful_shutdown(worker)

    signal.signal(signal.SIGTERM, _handle_sig)
    signal.signal(signal.SIGINT, _handle_sig)

    try:
        worker.work()
    except Exception as exc:
        print(f"[worker] exception: {exc}", file=sys.stderr)
    finally:
        loop_mgr.stop()

if __name__ == "__main__":
    main()

