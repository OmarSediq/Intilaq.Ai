from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.cv_schema import AwardsRequest, AwardResponse
from backend.utils.response_schemas import success_response, error_response
from backend.data_access.postgres.cv.award_repository import AwardRepository
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository

class CVAwardService:
    def __init__(self, db: AsyncSession, award_repo: AwardRepository, header_repo: CVHeaderRepository):
        self.db = db
        self.award_repo = award_repo
        self.header_repo = header_repo

    async def create(self, user_id: int, request: AwardsRequest):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(404, "Header not found for this user.")

        award = await self.award_repo.create({
            **request.dict(exclude={"header_id"}),
            "header_id": header.id
        })

        response_data = AwardResponse.model_validate(award)

        return success_response(201, data=response_data)


