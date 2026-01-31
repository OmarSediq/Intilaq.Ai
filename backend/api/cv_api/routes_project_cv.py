from fastapi import APIRouter, Depends
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.core.providers.domain_providers.cv_providers import  get_cv_project_service
from backend.schemas.cv_schema import ProjectRequest, ProjectDescriptionSaveRequest
from backend.domain_services.cv_services.cv_project_service import CVProjectService

router = APIRouter()

@router.post("/api/projects/", tags=["CV - Designer-Assistant"])
async def create_project(
    request: ProjectRequest,
    user = Depends(get_current_user),
    service = Depends(get_cv_project_service)
):
    return await service.create(request, user["user_id"])


@router.get("/api/projects/generate-description/{project_id}/", tags=["CV - Designer-Assistant"])
async def generate_project_description(
    project_id: int,
    user = Depends(get_current_user),
    service = Depends(get_cv_project_service)
):
    return await service.generate_description(project_id, user["user_id"])


@router.put("/api/projects/save-description/{project_id}/", tags=["CV - Designer-Assistant"])
async def save_project_description(
    project_id: int,
    request: ProjectDescriptionSaveRequest,
    user = Depends(get_current_user),
    service = Depends(get_cv_project_service)
):
    return await service.save_description(project_id, request, user["user_id"])
