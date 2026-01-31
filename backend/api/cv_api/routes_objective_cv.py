from fastapi import APIRouter, Depends
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.schemas.cv_schema import ObjectiveSaveRequest
from backend.domain_services.cv_services.cv_objective_service import CVObjectiveService
from backend.core.providers.domain_providers.cv_providers import get_cv_objective_service

router = APIRouter()



@router.post("/api/objectives/suggestions/",tags=["CV - Designer-Assistant"])
async def generate_objective_suggestions(
    request: ObjectiveSaveRequest, 
    user = Depends(get_current_user),
    service = Depends(get_cv_objective_service)
):
    return await service.generate_objective_suggestions(request, int(user["user_id"]))


@router.put("/api/objectives/save-description/{objective_id}/",tags=["CV - Designer-Assistant"])
async def save_objective_description(
    objective_id: int,
    request: ObjectiveSaveRequest,
    user = Depends(get_current_user),
    service = Depends(get_cv_objective_service)
):
    return await service.save_objective_description(objective_id, request.description, int(user["user_id"]))
