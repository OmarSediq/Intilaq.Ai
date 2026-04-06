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
    

    # async def download(self, file_id):
    #     stream = await self.bucket.open_download_stream(file_id)
    #     return await stream.read()


    # # -----------------------
    # # Existing PDF helpers (kept API compatible, now return str id)
    # # -----------------------
    # async def upload_pdf(self, filename: str, content: bytes, metadata: dict) -> str:
       
    #     metadata = metadata or {}
    #     metadata.setdefault("created_at", datetime.utcnow().isoformat())
    #     oid = await self.fs.upload_from_stream(filename, BytesIO(content), metadata=metadata)
    #     return str(oid)

    # async def download_pdf(self, file_id: str) -> bytes:
        
    #     oid = self._to_objectid(file_id)
    #     stream = await self.fs.open_download_stream(oid)
    #     return await stream.read()


    # async def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
      
    #     if self.db is None:
    #         raise RuntimeError("Mongo database instance (db) is required for metadata queries")
    #     oid = self._to_objectid(file_id)
    #     return await self.db["fs.files"].find_one({"_id": oid})

   
    # async def upload_html(
    #     self,
    #     filename: str,
    #     html_content: str,
    #     metadata: Optional[Dict[str, Any]] = None,
    #     gzip_compress: bool = True
    # ) -> str:
        
    #     data = html_content.encode("utf-8")
    #     if gzip_compress:
    #         buf = BytesIO()
    #         with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
    #             gz.write(data)
    #         payload = buf.getvalue()
    #         metadata = metadata or {}
    #         metadata["compressed"] = True
    #         metadata["content_encoding"] = "gzip"
    #     else:
    #         payload = data
    #         metadata = metadata or {}
    #         metadata["compressed"] = False

    #     metadata.setdefault("created_at", datetime.utcnow().isoformat())
    #     oid = await self.fs.upload_from_stream(filename, BytesIO(payload), metadata=metadata)
    #     return str(oid)

    # async def download_html(self, file_id: str) -> str:
        
    #     if self.db is None:
    #         raise RuntimeError("Mongo database instance (db) is required to read metadata")
    #     oid = self._to_objectid(file_id)
    #     stream = await self.fs.open_download_stream(oid)
    #     raw = await stream.read()
    #     file_doc = await self.db["fs.files"].find_one({"_id": oid})
    #     if not file_doc:
    #         raise FileNotFoundError(f"GridFS file {file_id} not found")
    #     meta = file_doc.get("metadata", {}) or {}
    #     if meta.get("content_encoding") == "gzip" or meta.get("compressed") is True:
    #         try:
    #             return gzip.decompress(raw).decode("utf-8")
    #         except (OSError, EOFError) as e:
    #             raise RuntimeError(f"Failed to decompress HTML file {file_id}: {e}")
    #     return raw.decode("utf-8")

    # # -----------------------
    # # Generic file helpers
    # # -----------------------
    # async def upload_file(self, filename: str, content: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
      
    #     metadata = metadata or {}
    #     metadata.setdefault("created_at", datetime.utcnow().isoformat())
    #     oid = await self.fs.upload_from_stream(filename, BytesIO(content), metadata=metadata)
    #     return str(oid)

    # async def download_file(self, file_id: str) -> bytes:
    #     oid = self._to_objectid(file_id)
    #     stream = await self.fs.open_download_stream(oid)
    #     return await stream.read()

    # # -----------------------
    # # Metadata / Queries
    # # -----------------------
    # async def find_files_for_user(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        
    #     if self.db is None:
    #         raise RuntimeError("Mongo database instance (db) is required for queries")
    #     cursor = self.db["fs.files"].find({"metadata.user_id": user_id}).sort("uploadDate", -1).limit(limit)
    #     return [doc async for doc in cursor]

    # async def delete_file(self, file_id: str) -> None:
    #     oid = self._to_objectid(file_id)
    #     await self.fs.delete(oid)

 
    # async def ensure_indexes(self):
        
    #     if self.db is None:
    #         raise RuntimeError("Mongo database instance (db) is required for ensure_indexes")
    #     await self.db["fs.files"].create_index([("metadata.user_id", 1)])
