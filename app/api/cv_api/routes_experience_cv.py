from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.api.auth_api.auth.routes_auth import get_current_user
from app.schemas.cv import ExperienceRequest, ExperienceSaveRequest
from app.services.cv_services.experience_services import (
    create_experience_service,
    get_experience_service,
    update_experience_service,
    delete_experience_service,
    generate_experience_suggestions_service,
    save_experience_description_service
)

router = APIRouter()


@router.post("/api/experiences/", tags=["Experience Management"])
async def create_experience(
    request: ExperienceRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_experience_service(request, int(user["user_id"]), db)


@router.get("/api/experiences/{experience_id}/", tags=["Experience Management"])
async def get_experience(
    experience_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_experience_service(experience_id, int(user["user_id"]), db)


# @router.put("/api/experiences/{experience_id}/", tags=["Experience Management"])
# async def update_experience(
#     experience_id: int,
#     request: ExperienceRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await update_experience_service(experience_id, request, int(user["user_id"]), db)


# @router.delete("/api/experiences/{experience_id}/", tags=["Experience Management"])
# async def delete_experience(
#     experience_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await delete_experience_service(experience_id, int(user["user_id"]), db)


@router.post("/api/experiences/suggestions/", tags=["AI Enhancements"])
async def generate_experience_suggestions(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await generate_experience_suggestions_service(int(user["user_id"]), db)


@router.put("/api/experiences/save-description/{experience_id}/", tags=["AI Enhancements"])
async def save_experience_description(
    experience_id: int,
    request: ExperienceSaveRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await save_experience_description_service(
        experience_id,
        request.selected_description,
        int(user["user_id"]),
        db
    )
