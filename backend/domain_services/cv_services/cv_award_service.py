from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.cv_schema import AwardsRequest
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

        return success_response(201, data=award)

    async def get(self, award_id: int, user_id: int):
        award = await self.award_repo.get_by_id(award_id)
        if not award:
            return error_response(404, "Award not found")

        header = await self.header_repo.get_by_id(award.header_id)
        if not header or header.user_id != user_id:
            return error_response(403, "Unauthorized access")

        return success_response(200, data=award)

    async def delete(self, award_id: int, user_id: int):
        award = await self.award_repo.get_by_id(award_id)
        if not award:
            return error_response(404, "Award not found")

        header = await self.header_repo.get_by_id(award.header_id)
        if not header or header.user_id != user_id:
            return error_response(403, "Unauthorized")

        await self.award_repo.delete(award)
        return success_response(200, {"message": "Award deleted successfully"})
