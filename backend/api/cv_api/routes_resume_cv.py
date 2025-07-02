from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.domain_services.cv_services.cv_resume_export_service import CVResumeExportService
from backend.core.providers.domain_providers.cv_providers import get_resume_export_service

router = APIRouter()

@router.get("/api/generate-cv/", response_class=HTMLResponse, tags=["CV - Designer-Assistant"])
async def generate_cv(user=Depends(get_current_user), service: CVResumeExportService = Depends(get_resume_export_service)):
    return await service.generate_html_image(user["user_id"])

@router.get("/api/download-cv/pdf/", tags=["CV - Designer-Assistant"])
async def download_and_store_cv_pdf(user=Depends(get_current_user), service: CVResumeExportService = Depends(get_resume_export_service)):
    return await service.generate_pdf_and_store(user["user_id"])

@router.get("/api/download-cv/docx/", tags=["CV - Designer-Assistant"])
async def download_cv_docx(user=Depends(get_current_user), service: CVResumeExportService = Depends(get_resume_export_service)):
    return await service.generate_docx(user["user_id"])

@router.get("/api/resumes/{file_id}/download", tags=["CV - Designer-Assistant"])
async def download_resume_from_mongo(file_id: str, user=Depends(get_current_user), service: CVResumeExportService = Depends(get_resume_export_service)):
    return await service.download_from_gridfs(file_id, user["user_id"])

@router.get("/api/regenerate-cv/", response_class=HTMLResponse, tags=["CV - Designer-Assistant"])
async def regenerate_cv(
    user: dict = Depends(get_current_user),
    service: CVResumeExportService = Depends(get_resume_export_service)
):
    return await service.generate_html(user["user_id"])