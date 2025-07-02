from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from io import BytesIO
from bson import ObjectId

class ResumeDownloadRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.db = mongo_client["resumes_db"]
        self.fs = AsyncIOMotorGridFSBucket(self.db)

    async def get_latest_resume_file(self, user_id: int):
        return await self.db["fs.files"].find_one(
            {"metadata.user_id": user_id},
            sort=[("uploadDate", -1)]
        )

    async def read_file_content(self, file_id: ObjectId) -> bytes:
        stream = await self.fs.open_download_stream(file_id)
        return await stream.read()
