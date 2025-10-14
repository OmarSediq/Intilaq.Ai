# backend/core/job_dispatchers/video_dispatcher.py
import uuid
import asyncio
from datetime import datetime
import inspect
import os
import logging
from pymongo import ReturnDocument
from bson import ObjectId
from typing import Union

from backend.core.base_service import TraceableService
from backend.core.providers.queue_provider import get_queue
from backend.core.providers.infra_providers import get_mongo_client_raw
from backend.data_access.mongo.task.tasks_repository import TasksRepository

from backend.data_access.mongo.gridfs_loader import GridFSLoader

logger = logging.getLogger("video_dispatcher")


class VideoDispatcherService(TraceableService):
    def __init__(self, db, hr_db_name: str = "hr_db"):
        """
        NOTE: __init__ is synchronous. Use create(...) async factory to obtain a ready instance.
        `db` should be either AsyncIOMotorDatabase or AsyncIOMotorClient; TasksRepository ctor will handle it.
        """
        self.queue = get_queue(name="video")
        self.tasks_repo = TasksRepository(db=db, db_name=hr_db_name)

    @classmethod
    async def create(cls, hr_db_name: str = "hr_db"):
        """
        Async factory: resolves mongo client (sync or coroutine), selects hr_db, and returns instance.
        """
        client_or_coro = get_mongo_client_raw()
        if inspect.isawaitable(client_or_coro):
            client = await client_or_coro
        else:
            client = client_or_coro

        # select db robustly
        try:
            db = client[hr_db_name]
        except Exception:
            try:
                db = client.get_database(hr_db_name)
            except Exception:
                db = client

        return cls(db=db, hr_db_name=hr_db_name)

    async def dispatch_video_processing(
        self,
        video_file_id: Union[str, ObjectId],
        interview_token: str,
        user_email: str,
        question_index: int,
    ) -> str:
        """
        Create a task (idempotent) and enqueue it. Returns job_id (existing or new).

        We store a small JSON payload in GridFS (payload_ref -> JSON file _id).
        This avoids worker trying to decode a binary video file as JSON.
        """
        # Normalize & validate incoming video_file_id -> ObjectId
        try:
            video_oid = (
                video_file_id
                if isinstance(video_file_id, ObjectId)
                else ObjectId(str(video_file_id).strip().replace("gridfs://", "", 1))
            )
        except Exception as exc:
            logger.exception("invalid video_file_id passed to dispatcher: %s", video_file_id)
            raise ValueError(f"invalid video_file_id for GridFS: {video_file_id}") from exc

        # idempotency key tied to the video (so we don't enqueue duplicate processing for same video)
        idempotency_key = f"video:{str(video_oid)}"

        # Build small JSON payload for the worker (can include context)
        payload_obj = {
            "video_file_id": str(video_oid),
            "interview_token": interview_token,
            "user_email": user_email,
            "question_index": question_index,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Save JSON payload into GridFS (using instance of GridFSLoader)
        try:
            loader = GridFSLoader()
            payload_file_id_str = await loader.save_json_to_gridfs_async(
                payload_obj,
                filename=f"payload_for_video_{str(video_oid)}.json"
            )
            # convert to ObjectId for storage consistency where possible
            try: 
                payload_ref = ObjectId(payload_file_id_str)
            except Exception:
                # fallback: store as string if conversion fails
                payload_ref = payload_file_id_str

        except Exception as exc:
            logger.exception("failed to save JSON payload to GridFS for video=%s: %s", video_oid, exc)
            raise

        now = datetime.utcnow()
        job_id = uuid.uuid4().hex

        on_insert = {
            "_id": job_id,
            "type": "video_processing",
            "status": "pending",
            "payload_ref": payload_ref,  # points to JSON file in GridFS (not the video binary)
            "attempts": 0,
            "max_attempts": int(os.environ.get("TASK_MAX_ATTEMPTS", "5")),
            "idempotency_key": idempotency_key,
            "created_at": now,
            "updated_at": now,
            "context": {
                "interview_token": interview_token,
                "user_email": user_email,
                "question_index": question_index,
            },
        }

        filter_q = {"idempotency_key": idempotency_key}

        # atomic upsert: if exists, returns existing doc, otherwise inserts and returns it
        inserted_doc = await self.tasks_repo.col.find_one_and_update(
            filter_q,
            {"$setOnInsert": on_insert},
            return_document=ReturnDocument.AFTER,
            upsert=True,
        )

        job_id_to_use = str(inserted_doc["_id"])

        # If task already queued/processing/succeeded we may return existing id immediately
        if inserted_doc.get("status") not in ("pending",):
            return job_id_to_use

        # enqueue in background thread to avoid blocking event loop (queue.enqueue is sync)
        try:
            await asyncio.to_thread(
                self.queue.enqueue,
                "backend.core.job_processors.process_video_pipeline_job.process_job_wrapper",
                job_id_to_use,
            )
            await self.tasks_repo.col.update_one(
                {"_id": inserted_doc["_id"]},
                {"$set": {"status": "queued", "queued_at": datetime.utcnow(), "updated_at": datetime.utcnow()}},
            )
            return job_id_to_use

        except Exception as exc:
            # Mark failed with reason so someone can inspect (or retry later)
            await self.tasks_repo.mark_failed(job_id_to_use, reason=f"enqueue_failed:{str(exc)}")
            logger.exception("enqueue failed for job=%s payload=%s: %s", job_id_to_use, payload_ref, exc)
            raise
