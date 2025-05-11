from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.api.auth_api.auth.routes_auth import get_current_user
from app.schemas.cv import EducationRequest
from app.services.cv_services.education_services import (
    create_education_service,
    get_education_service,
    update_education_service,
    delete_education_service
)

router = APIRouter()

@router.post("/api/educations/", tags=["Education Management"])
async def create_education(
    request: EducationRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_education_service(request, int(user["user_id"]), db)


# @router.get("/api/educations/{education_id}/", tags=["Education Management"])
# async def get_education(
#     education_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await get_education_service(education_id, int(user["user_id"]), db)


# @router.put("/api/educations/{education_id}/", tags=["Education Management"])
# async def update_education(
#     education_id: int,
#     request: EducationRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await update_education_service(education_id, request, int(user["user_id"]), db)


# @router.delete("/api/educations/{education_id}/", tags=["Education Management"])
# async def delete_education(
#     education_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await delete_education_service(education_id, int(user["user_id"]), db)
