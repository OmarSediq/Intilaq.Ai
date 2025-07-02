from fastapi import APIRouter, Depends
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.core.providers.domain_providers.cv_providers import get_cv_volunteering_service
from backend.schemas.cv_schema import VolunteeringRequest, SaveVolunteeringRequest, GenerateVolunteeringRequest
from backend.domain_services.cv_services.cv_volunteering_service import CVVolunteeringService

router = APIRouter()

@router.post("/api/volunteerings/", tags=["CV - Designer-Assistant"])
async def create_volunteering(
    request: VolunteeringRequest,
    user=Depends(get_current_user),
    service: CVVolunteeringService = Depends(get_cv_volunteering_service)
):
    return await service.create(request, user["user_id"])

@router.get("/api/volunteerings-suggestions/{volunteering_id}/", tags=["CV - Designer-Assistant"])
async def generate_volunteering_suggestions(
    volunteering_id : int,
    user=Depends(get_current_user),
    service: CVVolunteeringService = Depends(get_cv_volunteering_service)
):
    return await service.generate_suggestions(volunteering_id, user["user_id"])


@router.put("/api/volunteerings-save-description/{volunteering_id}/", tags=["CV - Designer-Assistant"])
async def save_volunteering_description(
    volunteering_id: int,
    request: SaveVolunteeringRequest,
    user=Depends(get_current_user),
    service: CVVolunteeringService = Depends(get_cv_volunteering_service)
):
    return await service.save_description(volunteering_id, request.selected_description, user["user_id"])
