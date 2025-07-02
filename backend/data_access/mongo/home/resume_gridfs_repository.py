from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from fastapi import UploadFile
from fastapi.responses import StreamingResponse
from bson import ObjectId
from datetime import datetime
from io import BytesIO


class ResumeGridFSRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.fs = AsyncIOMotorGridFSBucket(mongo_client["resumes_db"])
        self.db = mongo_client["resumes_db"]

    async def save_pdf(self, file: UploadFile, user_id: str, resume_name: str):
        content = await file.read()
        metadata = {
            "user_id": user_id,
            "resume_name": resume_name,
            "uploaded_at": datetime.utcnow()
        }
        return await self.fs.upload_from_stream(file.filename, content, metadata=metadata)

    async def get_pdf(self, file_id: str):
        stream = await self.fs.open_download_stream(ObjectId(file_id))
        content = await stream.read()
        return StreamingResponse(BytesIO(content), media_type="application/pdf")
