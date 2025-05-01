from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.schemas.cv import ObjectiveSaveRequest
from app.services.cv_services.objective_services import (
    generate_objective_suggestions_service,
    save_objective_description_service
)

router = APIRouter()


@router.post("/api/objectives/suggestions/", tags=["AI Enhancements"])
async def generate_objective_suggestions(
    request: ObjectiveSaveRequest, 
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await generate_objective_suggestions_service(request, int(user["user_id"]), db)


@router.put("/api/objectives/save-description/{objective_id}/", tags=["AI Enhancements"])
async def save_objective_description(
    objective_id: int,
    request: ObjectiveSaveRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await save_objective_description_service(objective_id, request.description, int(user["user_id"]), db)
