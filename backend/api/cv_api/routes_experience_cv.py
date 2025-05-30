from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.domain_providers.cv_providers import  get_cv_experience_service
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.schemas.cv_schema import ExperienceRequest, ExperienceSaveRequest
from backend.domain_services.cv_services.cv_experience_service import CVExperienceService

router = APIRouter()


@router.post("/api/experiences/", tags=["Experience Management"])
async def create_experience(
    request: ExperienceRequest,
    user: dict = Depends(get_current_user),
    service: CVExperienceService = Depends(get_cv_experience_service)
):
    return await service.create(request, int(user["user_id"]))


# @router.get("/api/experiences/{experience_id}/", tags=["Experience Management"])
# async def get_experience(
#     experience_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVExperienceService = Depends(get_cv_experience_service)
# ):
#     return await service.get(experience_id, int(user["user_id"]))


@router.post("/api/experiences/suggestions/", tags=["AI Enhancements"])
async def generate_experience_suggestions(
    user: dict = Depends(get_current_user),
    service: CVExperienceService = Depends(get_cv_experience_service)
):
    return await service.generate_suggestions(int(user["user_id"]))


@router.put("/api/experiences/save-description/{experience_id}/", tags=["AI Enhancements"])
async def save_experience_description(
    experience_id: int,
    request: ExperienceSaveRequest,
    user: dict = Depends(get_current_user),
    service: CVExperienceService = Depends(get_cv_experience_service)
):
    return await service.save_description(experience_id, request.selected_description, int(user["user_id"]))


# @router.put("/api/experiences/{experience_id}/", tags=["Experience Management"])
# async def update_experience(
#     experience_id: int,
#     request: ExperienceRequest,
#     user: dict = Depends(get_current_user),
#     service: CVExperienceService = Depends(get_cv_experience_service)
# ):
#     return await service.update(experience_id, request, int(user["user_id"]))


# @router.delete("/api/experiences/{experience_id}/", tags=["Experience Management"])
# async def delete_experience(
#     experience_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVExperienceService = Depends(get_cv_experience_service)
# ):
#     return await service.delete(experience_id, int(user["user_id"]))
