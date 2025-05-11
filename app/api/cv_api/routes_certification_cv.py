from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.schemas.cv import CertificationRequest, CertificationUpdateRequest
from app.services.cv_services.certification_services import (
    create_certification_service,
    get_certification_service,
    update_certification_service,
    delete_certification_service
)

router = APIRouter()

@router.post("/api/certifications/", tags=["Projects & Certifications"])
async def create_certification(
    request: CertificationRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_certification_service(request, user["user_id"], db)


# @router.get("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
# async def get_certification(
#     certification_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await get_certification_service(certification_id, user["user_id"], db)


# @router.put("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
# async def update_certification(
#     certification_id: int,
#     request: CertificationUpdateRequest,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await update_certification_service(certification_id, request, user["user_id"], db)


# @router.delete("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
# async def delete_certification(
#     certification_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     return await delete_certification_service(certification_id, user["user_id"], db)
