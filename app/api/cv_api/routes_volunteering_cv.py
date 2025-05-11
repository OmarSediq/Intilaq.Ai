from fastapi import APIRouter, Depends
from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.schemas.cv import VolunteeringRequest, SaveVolunteeringRequest, GenerateVolunteeringRequest
from app.services.cv_services.volunteering_services import (
    create_volunteering_service,
    get_volunteering_service,
    delete_volunteering_service,
    generate_volunteering_suggestions_service,
    save_volunteering_description_service
)

router = APIRouter()

@router.post("/api/volunteerings/", tags=["Volunteering & Awards"])
async def create_volunteering(request: VolunteeringRequest, user=Depends(get_current_user), db=Depends(get_db)):
    return await create_volunteering_service(request, user["user_id"], db)

# @router.get("/api/volunteerings/{volunteering_id}/", tags=["Volunteering & Awards"])
# async def get_volunteering(volunteering_id: int, user=Depends(get_current_user), db=Depends(get_db)):
#     return await get_volunteering_service(volunteering_id, user["user_id"], db)

# @router.delete("/api/volunteerings/{volunteering_id}/", tags=["Volunteering & Awards"])
# async def delete_volunteering(volunteering_id: int, user=Depends(get_current_user), db=Depends(get_db)):
#     return await delete_volunteering_service(volunteering_id, user["user_id"], db)

@router.post("/api/volunteerings-suggestions/", tags=["AI Enhancements"])
async def generate_volunteering_suggestions(request: GenerateVolunteeringRequest, user=Depends(get_current_user), db=Depends(get_db)):
    return await generate_volunteering_suggestions_service(request.volunteering_id, user["user_id"], db)

@router.put("/api/volunteerings-save-description/{volunteering_id}/", tags=["AI Enhancements"])
async def save_volunteering_description(volunteering_id: int, request: SaveVolunteeringRequest, user=Depends(get_current_user), db=Depends(get_db)):
    return await save_volunteering_description_service(volunteering_id, request.selected_description, user["user_id"], db)
