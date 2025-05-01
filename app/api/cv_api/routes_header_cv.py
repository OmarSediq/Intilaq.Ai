from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.schemas.cv import HeaderRequest
from app.services.cv_services.header_services import (
    create_header_service,
    get_header_service,
    update_header_service,
    delete_header_service
)

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
    db: AsyncSession = Depends(get_db)
):
    return await create_header_service(request, int(user["user_id"]), db)


@router.get("/api/headers/{header_id}/", tags=["Personal Information"])
async def get_header(
    header_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_header_service(header_id, int(user["user_id"]), db)


@router.put("/api/headers/{header_id}/", tags=["Personal Information"])
async def update_header(
    header_id: int,
    request: HeaderRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await update_header_service(header_id, request, int(user["user_id"]), db)


@router.delete("/api/headers/{header_id}/", tags=["Personal Information"])
async def delete_header(
    header_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await delete_header_service(header_id, int(user["user_id"]), db)
