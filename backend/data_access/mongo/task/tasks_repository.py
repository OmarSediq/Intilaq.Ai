# backend/core/db/tasks_repo.py
from typing import Optional, Any, Dict, Union
from datetime import datetime
from backend.core.base_service import TraceableService
from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from bson import ObjectId

from backend.core.providers.infra_providers import get_mongo_client_raw

class TasksRepository(TraceableService):
    def __init__(self,
                 db: Optional[Union[AsyncIOMotorDatabase, AsyncIOMotorClient]] = None,
                 db_name: str = "hr_db"):
        # choose database explicitly and deterministically
        if db is None:
            client = get_mongo_client_raw()
            # client is expected to be AsyncIOMotorClient singleton
            self.db: AsyncIOMotorDatabase = client[db_name]
        else:
            # caller passed either a client or a database
            if isinstance(db, AsyncIOMotorClient):
                self.db = db[db_name]
            else:
                # assume AsyncIOMotorDatabase
                self.db = db

        # collection for tasks
        self.col = self.db.get_collection("tasks")

    async def ensure_indexes(self):
        # create indexes commonly used by the pipeline
        await self.col.create_index("idempotency_key")
        await self.col.create_index("status")
        await self.col.create_index("created_at")
        # index payload_ref if stored as ObjectId or string
        await self.col.create_index("payload_ref")

    async def insert_task(self, task_doc: Dict[str, Any]):
        await self.col.insert_one(task_doc)

    async def get_task(self, job_id: str) -> Optional[Dict[str, Any]]:
        return await self.col.find_one({"_id": job_id})

    async def get_and_mark_processing(self, job_id: str) -> Optional[Dict[str, Any]]:
        now = datetime.utcnow()
        res = await self.col.find_one_and_update(
            {"_id": job_id, "status": {"$in": ["pending", "queued"]}},
            {"$set": {"status": "processing", "processing_started_at": now, "updated_at": now}},
            return_document=ReturnDocument.AFTER
        )
        return res

    async def mark_succeeded(self, job_id: str, result_ref: Optional[str] = None):
        await self.col.update_one(
            {"_id": job_id},
            {"$set": {"status": "succeeded", "result_ref": result_ref, "updated_at": datetime.utcnow()}}
        )

    async def increment_attempts(self, job_id: str) -> int:
        res = await self.col.find_one_and_update(
            {"_id": job_id},
            {"$inc": {"attempts": 1}, "$set": {"updated_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER
        )
        return res.get("attempts", 0) if res else 0

    async def mark_failed(self, job_id: str, reason: str = ""):
        await self.col.update_one(
            {"_id": job_id},
            {"$set": {"status": "failed", "failed_reason": reason, "updated_at": datetime.utcnow()}}
        )
