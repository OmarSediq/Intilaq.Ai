from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from app.services.db_services import get_user_by_header_id, generate_docx_from_html
from app.database.models.cv_section_models import Header
from app.utils.response_schemas import error_response
from app.core.config import env
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.future import select
from bson import ObjectId
from datetime import datetime
import pdfkit
import io
from io import BytesIO
from fastapi import HTTPException


class CVResumeExportService:
    def __init__(self, db_sql: AsyncSession, mongo_client: AsyncIOMotorClient):
        self.db = db_sql
        self.mongo = mongo_client
        self.env = env
        self.config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")

    async def _get_header_id(self, user_id: int):
        stmt = select(Header.id).where(Header.user_id == int(user_id))
        result = await self.db.execute(stmt)
        header_id = result.scalar()
        if not header_id:
            raise HTTPException(status_code=404, detail="No header associated with this user")
        return header_id

    def _safe_get(self, data, key, default=""):
        return data.get(key, default) if data.get(key) is not None else default

    async def generate_html(self, user_id: int):
        try:
            header_id = await self._get_header_id(user_id)
            user_data = await get_user_by_header_id(self.db, header_id)

            if not user_data or int(user_data["user_id"]) != int(user_id):
                return error_response(code=403, error_message="You do not have permission")

            template = self.env.get_template("resume_template.html")
            html_content = template.render(**{
                k: self._safe_get(user_data, k, []) if isinstance(v, list) else self._safe_get(user_data, k)
                for k, v in user_data.items()
            })

            return HTMLResponse(content=html_content)

        except Exception as e:
            return error_response(code=500, error_message=f"Template rendering error: {str(e)}")

    async def generate_pdf_and_store(self, user_id: int):
        try:
            header_id = await self._get_header_id(user_id)
            user_data = await get_user_by_header_id(self.db, header_id)

            template = self.env.get_template("resume_template.html")
            html_content = template.render(**user_data)

            pdf_bytes = pdfkit.from_string(html_content, False, options={
                "page-size": "A4", "margin-top": "10mm", "margin-right": "10mm",
                "margin-bottom": "10mm", "margin-left": "10mm", "encoding": "UTF-8",
                "dpi": 300, "enable-local-file-access": None
            }, configuration=self.config)

            mongo_db = self.mongo["resumes_db"]
            fs = AsyncIOMotorGridFSBucket(mongo_db)
            metadata = {
                "user_id": user_id,
                "resume_name": user_data.get("full_name", "Generated_CV"),
                "uploaded_at": datetime.utcnow()
            }

            file_id = await fs.upload_from_stream(
                f"{metadata['resume_name']}.pdf",
                BytesIO(pdf_bytes),
                metadata=metadata
            )

            return StreamingResponse(
                BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={metadata['resume_name']}.pdf",
                    "X-File-ID": str(file_id)
                }
            )
        except Exception as e:
            return error_response(code=500, error_message=f"PDF generation error: {str(e)}")

    async def generate_docx(self, user_id: int):
        try:
            header_id = await self._get_header_id(user_id)
            user_data = await get_user_by_header_id(self.db, header_id)

            template = self.env.get_template("resume_template.html")
            html_content = template.render(**user_data)

            docx_buffer = await generate_docx_from_html(html_content)

            return StreamingResponse(
                docx_buffer,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f"attachment; filename={user_data.get('full_name', 'Generated_CV')}.docx"}
            )
        except Exception as e:
            return error_response(code=500, error_message=f"DOCX generation error: {str(e)}")

    async def download_from_gridfs(self, file_id: str, user_id: int):
        try:
            mongo_db = self.mongo["resumes_db"]
            file_doc = await mongo_db["fs.files"].find_one({"_id": ObjectId(file_id)})

            if not file_doc:
                return error_response(code=404, error_message="File not found")

            user_id_from_file = str(file_doc.get("metadata", {}).get("user_id"))
            if user_id_from_file != str(user_id):
                return error_response(code=403, error_message="You do not have access to this file")

            fs = AsyncIOMotorGridFSBucket(mongo_db)
            stream = await fs.open_download_stream(ObjectId(file_id))
            content = await stream.read()

            return StreamingResponse(
                io.BytesIO(content),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={file_doc.get('filename', 'cv')}.pdf"}
            )
        except Exception as e:
            return error_response(code=500, error_message=f"Error fetching resume: {str(e)}")
