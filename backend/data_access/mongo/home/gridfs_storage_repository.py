from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from bson import ObjectId
from io import BytesIO

from backend.core.base_service import TraceableService


class GridFSStorageService (TraceableService):
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.fs = AsyncIOMotorGridFSBucket(mongo_client["resumes_db"])
        self.mongo = mongo_client

    async def upload_pdf(self, filename: str, content: bytes, metadata: dict):
        return await self.fs.upload_from_stream(filename, BytesIO(content), metadata=metadata)

    async def download_pdf(self, file_id: str) -> bytes:
        stream = await self.fs.open_download_stream(ObjectId(file_id))
        return await stream.read()

    async def get_file_metadata(self, file_id: str):
        return await self.mongo["resumes_db"]["fs.files"].find_one({"_id": ObjectId(file_id)})
