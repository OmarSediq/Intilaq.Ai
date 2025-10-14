# backend/data_access/mongo/hr/hr_interview_gridfs_repository.py
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorGridFSBucket,
    AsyncIOMotorGridOut,
)
from bson import ObjectId
import io
import asyncio
from typing import Optional, Union

from backend.core.base_service import TraceableService


class HRGridFSStorageService(TraceableService):
    def __init__(self, db: AsyncIOMotorDatabase):
        # don't create bucket here (no running loop guaranteed)
        self._db = db
        self._bucket: Optional[AsyncIOMotorGridFSBucket] = None

    def _check_async_context(self) -> None:
        """
        Raise helpful error if called outside an async context.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError as exc:
            raise RuntimeError(
                "_ensure_bucket / GridFS methods must be called from an async context (running event loop)."
            ) from exc

    def _ensure_bucket(self) -> AsyncIOMotorGridFSBucket:
        """
        Lazily create the AsyncIOMotorGridFSBucket.
        Must be called from inside an async function.
        """
        # ensure we are in an async context (running loop)
        self._check_async_context()

        if self._bucket is None:
            # This constructor reads the current event loop internally — safe now.
            self._bucket = AsyncIOMotorGridFSBucket(self._db)
        return self._bucket

    async def get_video_by_file_id(self, file_id: Union[str, ObjectId]) -> bytes:
        """
        Return raw bytes of the video. Raises ValueError for invalid id and
        FileNotFoundError if the file is missing.
        """
        try:
            oid = file_id if isinstance(file_id, ObjectId) else ObjectId(str(file_id))
        except Exception as exc:
            raise ValueError(f"invalid file_id: {file_id}") from exc

        bucket = self._ensure_bucket()
        grid_out: Optional[AsyncIOMotorGridOut] = None
        try:
            grid_out = await bucket.open_download_stream(oid)
            data = await grid_out.read()
            return data
        except Exception as exc:
            # re-raise with clearer message (caller can catch FileNotFoundError if desired)
            raise
        finally:
            try:
                if grid_out is not None:
                    await grid_out.close()
            except Exception:
                pass

    async def save_video(self, filename: str, file_stream) -> str:
        """
        Upload file-like object or bytes and return file id (str).
        Accepts raw bytes or file-like objects.
        """
        bucket = self._ensure_bucket()

        # Normalize input: bytes -> BytesIO; else assume file-like
        if isinstance(file_stream, (bytes, bytearray)):
            stream = io.BytesIO(file_stream)
            oid = await bucket.upload_from_stream(filename, stream)
        else:
            # assume file-like object with read() — motor should accept it when in async loop
            oid = await bucket.upload_from_stream(filename, file_stream)

        return str(oid)

    async def save_audio(self, filename: str, file_bytes: bytes) -> str:
        stream = io.BytesIO(file_bytes)
        bucket = self._ensure_bucket()
        oid = await bucket.upload_from_stream(filename, stream)
        return str(oid)

    async def upload_video(self, filename: str, file_stream) -> str:
        """
        Alias for save_video (backwards compat).
        """
        return await self.save_video(filename, file_stream)
