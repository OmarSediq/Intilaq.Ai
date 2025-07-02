import tempfile

import imgkit
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
import io

from starlette.responses import FileResponse

from backend.utils.response_schemas import error_response
from backend.data_access.postgres.cv.resume_repository import ResumeRepository
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.domain_services.doc_services.resume_html_renderer import ResumeHTMLRenderer
from backend.domain_services.doc_services.pdf_generator_service import PDFGeneratorService
from backend.domain_services.doc_services.docx_generator_services import DocxGenerator
from backend.data_access.mongo.home.gridfs_storage_repository import GridFSStorageService


class CVResumeExportService:
    def __init__(
        self,
        db_sql: AsyncSession,
        resume_repo: ResumeRepository,
        html_renderer: ResumeHTMLRenderer,
        pdf_generator: PDFGeneratorService,
        docx_generator: DocxGenerator,
        gridfs_storage: GridFSStorageService,
        header_repo: CVHeaderRepository,
    ):
        self.db = db_sql
        self.resume_repo = resume_repo
        self.html_renderer = html_renderer
        self.pdf_generator = pdf_generator
        self.docx_generator = docx_generator
        self.storage = gridfs_storage
        self.header_repo = header_repo

    async def generate_html_image(self, user_id: int):
        try:
            header_id = await self.header_repo.get_header_id_by_user_id(user_id)
            if not header_id:
                raise HTTPException(status_code=404, detail="No header associated with this user")

            user_data = await self.resume_repo.get_user_by_header_id(header_id)
            if not user_data or int(user_data["user_id"]) != int(user_id):
                return error_response(code=403, error_message="You do not have permission")

            html_content = self.html_renderer.render(user_data)

            options = {
                'format': 'png',
                'width': '800',
                'disable-smart-width': '',
            }


            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                imgkit.from_string(html_content, tmp_file.name, options=options)
                image_path = tmp_file.name
            return FileResponse(
                image_path,
                media_type="image/png",
                filename="cv_snapshot.png"
            )

        except Exception as e:
            return error_response(code=500, error_message=f"Image rendering error: {str(e)}")

    async def generate_pdf_and_store(self, user_id: int):
        try:
            header_id = await self.header_repo.get_header_id_by_user_id(user_id)
            if not header_id:
                raise HTTPException(status_code=404, detail="No header associated with this user")

            user_data = await self.resume_repo.get_user_by_header_id(header_id)
            html_content = self.html_renderer.render(user_data)
            pdf_bytes = self.pdf_generator.generate(html_content)

            metadata = {
                "user_id": user_id,
                "resume_name": user_data.get("full_name", "Generated_CV"),
                "uploaded_at": datetime.utcnow()
            }

            file_id = await self.storage.upload_pdf(
                f"{metadata['resume_name']}.pdf",
                pdf_bytes,
                metadata
            )

            return StreamingResponse(
                io.BytesIO(pdf_bytes),
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
            header_id = await self.header_repo.get_header_id_by_user_id(user_id)
            if not header_id:
                raise HTTPException(status_code=404, detail="No header associated with this user")

            user_data = await self.resume_repo.get_user_by_header_id(header_id)
            html_content = self.html_renderer.render(user_data)
            docx_buffer = await self.docx_generator.generate_from_html(html_content)

            return StreamingResponse(
                docx_buffer,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f"attachment; filename={user_data.get('full_name', 'Generated_CV')}.docx"}
            )

        except Exception as e:
            return error_response(code=500, error_message=f"DOCX generation error: {str(e)}")

    async def download_from_gridfs(self, file_id: str, user_id: int):
        try:
            file_doc = await self.storage.get_file_metadata(file_id)
            if not file_doc:
                return error_response(code=404, error_message="File not found")

            user_id_from_file = str(file_doc.get("metadata", {}).get("user_id"))
            if user_id_from_file != str(user_id):
                return error_response(code=403, error_message="You do not have access to this file")

            content = await self.storage.download_pdf(file_id)

            return StreamingResponse(
                io.BytesIO(content),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={file_doc.get('filename', 'cv')}.pdf"}
            )

        except Exception as e:
            return error_response(code=500, error_message=f"Error fetching resume: {str(e)}")
