from fastapi import APIRouter, Depends
from backend.core.providers.domain_providers.cv_providers import  get_cv_education_service
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.schemas.cv import EducationRequest
from backend.domain_services.cv_services.cv_education_service import CVEducationService

router = APIRouter()

@router.post("/api/educations/", tags=["Education Management"])
async def create_education(
    request: EducationRequest,
    user: dict = Depends(get_current_user),
    service: CVEducationService = Depends(get_cv_education_service)
):
    return await service.create(request, int(user["user_id"]))


@router.get("/api/educations/{education_id}/", tags=["Education Management"])
async def get_education(
    education_id: int,
    user: dict = Depends(get_current_user),
    service: CVEducationService = Depends(get_cv_education_service)
):
    return await service.get(education_id, int(user["user_id"]))


# @router.put("/api/educations/{education_id}/", tags=["Education Management"])
# async def update_education(
#     education_id: int,
#     request: EducationRequest,
#     user: dict = Depends(get_current_user),
#     service: CVEducationService = Depends(get_cv_education_service)
# ):
#     return await service.update(education_id, request, int(user["user_id"]))


# @router.delete("/api/educations/{education_id}/", tags=["Education Management"])
# async def delete_education(
#     education_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVEducationService = Depends(get_cv_education_service)
# ):
#     return await service.delete(education_id, int(user["user_id"]))
