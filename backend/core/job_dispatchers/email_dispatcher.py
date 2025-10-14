import inspect
import asyncio
from typing import Dict, Any
import logging
from backend.core.base_service import TraceableService
from backend.core.providers.queue_provider import get_queue
from backend.core.worker_service import loop_mgr
from backend.data_access.mongo.gridfs_loader import GridFSLoader
from backend.data_access.mongo.task.tasks_repository import TasksRepository
from backend.core.providers.infra_providers import get_mongo_db

logger = logging.getLogger("intilaqai.email_dispatcher")

class EmailDispatcherService(TraceableService):
    def __init__(self, queue_name: str | None = None):
        self.queue = get_queue(name=queue_name or "email")

    def dispatch_send_invitations(self, payload: Dict[str, Any]) -> str:
        # basic validation
        if not isinstance(payload, dict):
            raise TypeError("payload must be a dict")

        # ensure loop_mgr running (safe start)
        try:
            if not loop_mgr.is_ready():
                loop_mgr.start(wait_ready=True, timeout=10)
        except Exception as exc:
            logger.exception("loop_mgr failed to start: %s", exc)
            raise RuntimeError("background loop not available") from exc

        # save payload to GridFS
        try:
            loader = GridFSLoader()
            payload_ref = loop_mgr.run_coro_sync(loader.save_json_to_gridfs_async(payload), timeout=10)
        except Exception as exc:
            logger.exception("failed to save payload to GridFS: %s", exc)
            raise

        # create task doc robustly (support async or sync repo)
        repo = TasksRepository(db=get_mongo_db())
        task_doc = {
            "type": "send_invitation",
            "payload_ref": payload_ref,
            "status": "pending",
            "attempts": 0,
            "max_attempts": 5,
            "created_at": __import__("datetime").datetime.utcnow(),
            "owner": payload.get("hr_id"),
            "idempotency_key": payload.get("idempotency_key")
        }

        try:
            insert_task = getattr(repo, "insert_task", None)
            if insert_task is None:
                raise RuntimeError("repo.insert_task missing")
            if inspect.iscoroutinefunction(insert_task):
                job_id = loop_mgr.run_coro_sync(repo.insert_task(task_doc), timeout=5)
            else:
                # run sync insert in a thread within loop_mgr to avoid blocking background loop
                job_id = loop_mgr.run_coro_sync(asyncio.to_thread(repo.insert_task, task_doc), timeout=10)
        except Exception as exc:
            logger.exception("failed to insert task doc: %s", exc)
            raise

        # enqueue and mark failed on enqueue error
        try:
            self.queue.enqueue("backend.core.job_processors.process_send_invitation_job.send_invitation_job", str(job_id))
        except Exception as exc:
            logger.exception("failed to enqueue job %s: %s", job_id, exc)
            try:
                loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason=f"enqueue_failed:{str(exc)}"), timeout=5)
            except Exception:
                logger.exception("failed to mark task failed for job %s", job_id)
            raise

        return str(job_id)
