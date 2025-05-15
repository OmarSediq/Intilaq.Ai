from fastapi import APIRouter, Depends
from app.core.providers.domain_providers.user_provider import get_current_user
from app.core.providers.domain_providers.cv_providers import  get_cv_project_service
from app.schemas.cv import ProjectRequest, ProjectDescriptionSaveRequest
from app.domain_services.cv_services.cv_project_service import CVProjectService

router = APIRouter()

@router.post("/api/projects/", tags=["Projects & Certifications"])
async def create_project(
    request: ProjectRequest,
    user: dict = Depends(get_current_user),
    service: CVProjectService = Depends(get_cv_project_service)
):
    return await service.create(request, user["user_id"])


@router.post("/api/projects/generate-description/", tags=["AI Enhancements"])
async def generate_project_description(
    request: ProjectRequest,
    user: dict = Depends(get_current_user),
    service: CVProjectService = Depends(get_cv_project_service)
):
    return await service.generate_description(request, user["user_id"])


@router.put("/api/projects/save-description/{project_id}/", tags=["AI Enhancements"])
async def save_project_description(
    project_id: int,
    request: ProjectDescriptionSaveRequest,
    user: dict = Depends(get_current_user),
    service: CVProjectService = Depends(get_cv_project_service)
):
    return await service.save_description(project_id, request, user["user_id"])
