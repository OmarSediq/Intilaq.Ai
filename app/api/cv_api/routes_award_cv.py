from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.services.cv_services.award_services import (
    create_award_service,
    get_award_service,
    delete_award_service
)
from app.schemas.cv import AwardsRequest
from app.utils.response_schemas import success_response, serialize_sqlalchemy_object

router = APIRouter()

@router.post("/api/awards/", tags=["Volunteering & Awards"])
async def create_award(
    request: AwardsRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    award = await create_award_service(user["user_id"], request, db)
    return success_response(code=201, data={
        "message": "Award created successfully",
        "data": serialize_sqlalchemy_object(award)
    })


# @router.get("/api/awards/{award_id}/", tags=["Volunteering & Awards"])
# async def get_award(
#     award_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     award = await get_award_service(award_id, user["user_id"], db)
#     return success_response(code=200, data={"data": serialize_sqlalchemy_object(award)})


# @router.delete("/api/awards/{award_id}/", tags=["Volunteering & Awards"])
# async def delete_award(
#     award_id: int,
#     user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     await delete_award_service(award_id, user["user_id"], db)
#     return success_response(code=200, data={"message": "Award deleted successfully"})
