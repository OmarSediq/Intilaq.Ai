from fastapi import APIRouter, Depends
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.core.providers.domain_providers.cv_providers import get_cv_award_service
from backend.schemas.cv import AwardsRequest
from backend.domain_services.cv_services.cv_award_service import CVAwardService

router = APIRouter()

@router.post("/api/awards/", tags=["Volunteering & Awards"])
async def create_award(
    request: AwardsRequest,
    user: dict = Depends(get_current_user),
    service: CVAwardService = Depends(get_cv_award_service)
):
    return await service.create(user["user_id"], request)


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
