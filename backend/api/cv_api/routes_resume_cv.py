import io
from fastapi import APIRouter, Depends
from fastapi.responses import  HTMLResponse, StreamingResponse
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.domain_services.cv_services.cv_resume_export_service import CVResumeExportService
from backend.core.providers.domain_providers.cv_providers import get_resume_export_service
from backend.domain_services.cv_services.cv_download_service  import CVDownloadService
from backend.core.providers.domain_providers.cv_providers import get_cv_download_service
router = APIRouter()

@router.post("/api/cv/generate",tags=["CV - Designer-Assistant"])
async def generate_cv(user=Depends(get_current_user),service: CVResumeExportService = Depends(get_resume_export_service)):
    return await service.execute(user["user_id"])


@router.get("/api/download-cv/pdf/", tags=["CV - Designer-Assistant"])
async def download_pdf(user=Depends(get_current_user), service: CVDownloadService = Depends(get_cv_download_service)):
    file_bytes=  await service.download_pdf(user["user_id"])

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=cv.pdf"
        }
    )




@router.get("/api/download-cv/docx/", tags=["CV - Designer-Assistant"])
async def download_docx(user=Depends(get_current_user), service: CVDownloadService = Depends(get_cv_download_service)):
    file_bytes=  await service.download_docx(user["user_id"])

    return StreamingResponse(
    io.BytesIO(file_bytes),
    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    headers={
        "Content-Disposition": "attachment; filename=cv.docx"
    }
)


@router.get("/api/resumes/{file_id}/download", tags=["CV - Designer-Assistant"])
async def download_by_file_id(file_id: str, user=Depends(get_current_user), service: CVDownloadService = Depends(get_cv_download_service)):
    file_bytes =  await service.download_pdf_by_snapshot(file_id, user["user_id"])
    return StreamingResponse(
                io.BytesIO(file_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": "attachment; filename=cv.pdf"
                }
            )




@router.get("/api/regenerate-cv/", response_class=HTMLResponse, tags=["CV - Designer-Assistant"])

async def regenerate_cv(user=Depends(get_current_user),service: CVDownloadService = Depends(get_cv_download_service)):
    return await service.review_html(user["user_id"])




