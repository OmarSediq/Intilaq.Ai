from fastapi import APIRouter, Depends
from app.core.providers.services.user_provider import get_current_user
from app.core.providers.services.cv_providers import get_cv_award_service
from app.schemas.cv import AwardsRequest
from app.services.cv_services.cv_award_service import CVAwardService
from app.utils.response_schemas import success_response, serialize_sqlalchemy_object

router = APIRouter()

@router.post("/api/awards/", tags=["Volunteering & Awards"])
async def create_award(
    request: AwardsRequest,
    user: dict = Depends(get_current_user),
    service: CVAwardService = Depends(get_cv_award_service)
):
    award = await service.create(user["user_id"], request)
    return success_response(code=201, data={
        "message": "Award created successfully",
        "data": serialize_sqlalchemy_object(award)
    })


# @router.get("/api/awards/{award_id}/", tags=["Volunteering & Awards"])
# async def get_award(
#     award_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVAwardService = Depends(get_cv_award_service)
# ):
#     award = await service.get(award_id, user["user_id"])
#     return success_response(code=200, data={"data": serialize_sqlalchemy_object(award)})


# @router.delete("/api/awards/{award_id}/", tags=["Volunteering & Awards"])
# async def delete_award(
#     award_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVAwardService = Depends(get_cv_award_service)
# ):
#     await service.delete(award_id, user["user_id"])
#     return success_response(code=200, data={"message": "Award deleted successfully"})
