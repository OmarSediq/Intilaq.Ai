from fastapi.responses import StreamingResponse
from io import BytesIO
from backend.utils.response_schemas import error_response
from backend.data_access.mongo.home.resume_download_repository import ResumeDownloadRepository

class ResumeDownloadService:
    def __init__(self, repository: ResumeDownloadRepository):
        self.repo = repository

    async def download_latest_resume(self, user_id: int):
        try:
            file_doc = await self.repo.get_latest_resume_file(user_id)
            if not file_doc:
                return error_response(code=404, error_message="No resume found for this user")

            content = await self.repo.read_file_content(file_doc["_id"])

            return StreamingResponse(
                BytesIO(content),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={file_doc.get('filename', 'resume')}.pdf"}
            )
        except Exception as e:
            return error_response(code=500, error_message=f"Resume download error: {str(e)}")
