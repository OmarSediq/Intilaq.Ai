from fastapi import APIRouter, Depends
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.core.providers.domain_providers.cv_providers import  get_cv_certification_service
from backend.schemas.cv_schema import CertificationRequest
from backend.domain_services.cv_services.cv_certification_service import CVCertificationService

router = APIRouter()


@router.post("/api/certifications/", tags=["Projects & Certifications"])
async def create_certification(
    request: CertificationRequest,
    user: dict = Depends(get_current_user),
    service: CVCertificationService = Depends(get_cv_certification_service)
):
    return await service.create(request, user["user_id"])


# @router.get("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
# async def get_certification(
#     certification_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVCertificationService = Depends(get_cv_certification_service)
# ):
#     return await service.get(certification_id, user["user_id"])


# @router.put("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
# async def update_certification(
#     certification_id: int,
#     request: CertificationUpdateRequest,
#     user: dict = Depends(get_current_user),
#     service: CVCertificationService = Depends(get_cv_certification_service)
# ):
#     return await service.update(certification_id, request, user["user_id"])


# @router.delete("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
# async def delete_certification(
#     certification_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVCertificationService = Depends(get_cv_certification_service)
# ):
#     return await service.delete(certification_id, user["user_id"])
