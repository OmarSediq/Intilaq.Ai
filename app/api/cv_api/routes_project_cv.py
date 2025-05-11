from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.schemas.cv import ProjectRequest, ProjectDescriptionSaveRequest
from app.services.cv_services.project_services import (
    create_project_service,
    get_project_service,
    update_project_service,
    delete_project_service,
    generate_project_description_service,
    save_project_description_service
)

router = APIRouter()

@router.post("/api/projects/", tags=["Projects & Certifications"])
async def create_project(
    request: ProjectRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_project_service(request, user["user_id"], db)


# @router.get("/api/projects/{project_id}/", tags=["Projects & Certifications"])
# async def get_project(
#     project_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await get_project_service(project_id, user["user_id"], db)


# @router.put("/api/projects/{project_id}/", tags=["Projects & Certifications"])
# async def update_project(
#     project_id: int,
#     request: ProjectRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await update_project_service(project_id, request, user["user_id"], db)


# @router.delete("/api/projects/{project_id}/", tags=["Projects & Certifications"])
# async def delete_project(
#     project_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await delete_project_service(project_id, user["user_id"], db)


@router.post("/api/projects/generate-description/", tags=["AI Enhancements"])
async def generate_project_description(
    request: ProjectRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await generate_project_description_service(request, user["user_id"], db)


@router.put("/api/projects/save-description/{project_id}/", tags=["AI Enhancements"])
async def save_project_description(
    project_id: int,
    request: ProjectDescriptionSaveRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await save_project_description_service(project_id, request, user["user_id"], db)
