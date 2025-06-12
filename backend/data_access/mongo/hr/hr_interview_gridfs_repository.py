from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from bson import ObjectId
import io
from backend.core.base_service import TraceableService


class HRGridFSStorageService(TraceableService):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.gridfs_bucket = AsyncIOMotorGridFSBucket(db)

    async def get_video_by_file_id(self, file_id: str) -> bytes:
        grid_out = await self.gridfs_bucket.open_download_stream(ObjectId(file_id))
        return await grid_out.read()

    async def save_video(self, filename: str, file_stream) -> str:
        video_id = await self.gridfs_bucket.upload_from_stream(filename, file_stream)
        return str(video_id)

    async def save_audio(self, filename: str, file_bytes: bytes) -> str:
        stream = io.BytesIO(file_bytes)
        audio_id = await self.gridfs_bucket.upload_from_stream(filename, stream)
        return str(audio_id)

    async def upload_video(self, filename: str, file_stream) -> str:
        video_id = await self.gridfs_bucket.upload_from_stream(filename, file_stream)
        return str(video_id)