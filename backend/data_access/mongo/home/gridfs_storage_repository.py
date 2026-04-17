from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from bson import ObjectId, errors as bson_errors
from io import BytesIO
import gzip
from datetime import datetime

from backend.core.base_service import TraceableService


class GridFSStorageRepository(TraceableService):
   
    def __init__(self, bucket: AsyncIOMotorGridFSBucket, db: Optional[AsyncIOMotorDatabase] = None):
        self.fs = bucket
        self.db = db


    def _to_objectid(self, file_id: str) -> ObjectId:
        try:
            return ObjectId(file_id)
        except (bson_errors.InvalidId, TypeError) as e:
            raise ValueError(f"Invalid file_id '{file_id}': {e}")


    async def download(self, file_id):
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        stream = await self.fs.open_download_stream(file_id)
        return await stream.read()
    

    async def get_file_metadata(self, file_id: str) -> dict:

        if isinstance(file_id, str):
            file_id = ObjectId(file_id)

        file_doc = await self.db["fs.files"].find_one({"_id": file_id})

        if not file_doc:
            raise ValueError("File not found in GridFS")

        return file_doc
    
    async def get_file_by_snapshot(self, snapshot_id: str, file_type: str):
        file_doc = await self.db["fs.files"].find_one({
            "metadata.snapshot_id": snapshot_id,
            "metadata.type": file_type
        })

        if not file_doc:
            raise ValueError("File not found for this snapshot")

        return file_doc