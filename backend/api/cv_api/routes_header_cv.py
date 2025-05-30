from fastapi import APIRouter, Depends, Request, status, HTTPException
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.core.providers.domain_providers.cv_providers import get_cv_header_service
from backend.schemas.cv_schema import HeaderRequest
from backend.domain_services.cv_services.cv_header_service import CVHeaderService

router = APIRouter()

async def enforce_json_content_type(request: Request):
    if not request.headers.get("content-type", "").startswith("application/json"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported Media Type. Content-Type must be application/json."
        )

@router.post("/api/headers/", tags=["Personal Information"], dependencies=[Depends(enforce_json_content_type)])
async def create_header(
    request: HeaderRequest,
    user: dict = Depends(get_current_user),
    service: CVHeaderService = Depends(get_cv_header_service)
):
    return await service.create_header(request, int(user["user_id"]))


# @router.get("/api/headers/{header_id}", tags=["Personal Information"])
# async def get_header(
#     header_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVHeaderService = Depends(get_cv_header_service)
# ):
#     return await service.get_header(header_id, int(user["user_id"]))


# @router.put("/api/headers/{header_id}", tags=["Personal Information"])
# async def update_header(
#     header_id: int,
#     request: HeaderRequest,
#     user: dict = Depends(get_current_user),
#     service: CVHeaderService = Depends(get_cv_header_service)
# ):
#     return await service.update_header(header_id, request, int(user["user_id"]))


# @router.delete("/api/headers/{header_id}", tags=["Personal Information"])
# async def delete_header(
#     header_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVHeaderService = Depends(get_cv_header_service)
# ):
#     return await service.delete_header(header_id, int(user["user_id"]))
