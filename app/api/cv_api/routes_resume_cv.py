from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from app.core.providers.services.user_provider import get_current_user
from app.services.cv_services.cv_resume_export_service import CVResumeExportService
from app.core.providers.services.cv_providers import get_resume_export_service

router = APIRouter()

@router.get("/api/generate-cv/", response_class=HTMLResponse, tags=["CV Exporting"])
async def generate_cv(user=Depends(get_current_user), service: CVResumeExportService = Depends(get_resume_export_service)):
    return await service.generate_html(user["user_id"])

@router.get("/api/download-cv/pdf/", tags=["CV Exporting"])
async def download_and_store_cv_pdf(user=Depends(get_current_user), service: CVResumeExportService = Depends(get_resume_export_service)):
    return await service.generate_pdf_and_store(user["user_id"])

@router.get("/api/download-cv/docx/", tags=["CV Exporting"])
async def download_cv_docx(user=Depends(get_current_user), service: CVResumeExportService = Depends(get_resume_export_service)):
    return await service.generate_docx(user["user_id"])

@router.get("/api/resumes/{file_id}/download", tags=["My Resume"])
async def download_resume_from_mongo(file_id: str, user=Depends(get_current_user), service: CVResumeExportService = Depends(get_resume_export_service)):
    return await service.download_from_gridfs(file_id, user["user_id"])

@router.get("/api/regenerate-cv/", response_class=HTMLResponse, tags=["CV Exporting"])
async def regenerate_cv(
    user: dict = Depends(get_current_user),
    service: CVResumeExportService = Depends(get_resume_export_service)
):
    return await service.generate_html(user["user_id"])