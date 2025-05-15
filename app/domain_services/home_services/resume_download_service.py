from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.utils.response_schemas import error_response

class ResumeDownloadService:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.db = mongo_client["resumes_db"]

    async def download_latest_resume(self, user_id: int):
        try:
            file_doc = await self.db["fs.files"].find_one(
                {"metadata.user_id": int(user_id)},
                sort=[("uploadDate", -1)]
            )
            if not file_doc:
                return error_response(code=404, error_message="No resume found for this user")

            fs = AsyncIOMotorGridFSBucket(self.db)
            stream = await fs.open_download_stream(file_doc["_id"])
            content = await stream.read()

            return StreamingResponse(
                BytesIO(content),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={file_doc.get('filename', 'resume')}.pdf"}
            )
        except Exception as e:
            return error_response(code=500, error_message=f"Resume download error: {str(e)}")
