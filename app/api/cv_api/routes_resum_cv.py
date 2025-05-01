from fastapi import APIRouter, Depends
from fastapi.responses import  HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.services.mongo_services import get_mongo_client
from app.services.cv_services.resume_services import (
    generate_cv_html,
    generate_pdf_and_store,
    generate_docx_file,
    download_pdf_from_gridfs
)

router = APIRouter()

@router.get("/api/generate-cv/", response_class=HTMLResponse, tags=["CV Exporting"])
async def generate_cv(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await generate_cv_html(user["user_id"], db)

@router.get("/api/download-cv/pdf/", tags=["CV Exporting"])
async def download_and_store_cv_pdf(
    user: dict = Depends(get_current_user),
    db_sql: AsyncSession = Depends(get_db),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    return await generate_pdf_and_store(user["user_id"], db_sql, mongo_client)

@router.get("/api/download-cv/docx/", tags=["CV Exporting"])
async def download_cv_docx(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await generate_docx_file(user["user_id"], db)

@router.get("/api/regenerate-cv/", response_class=HTMLResponse, tags=["CV Exporting"])
async def regenerate_cv(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await generate_cv_html(user["user_id"], db)

@router.get("/api/resumes/{file_id}/download", tags=["My Resume"])
async def download_resume_from_mongo(
    file_id: str,
    user: dict = Depends(get_current_user),
    db = Depends(get_mongo_client)
):
    return await download_pdf_from_gridfs(file_id, user["user_id"], db)
