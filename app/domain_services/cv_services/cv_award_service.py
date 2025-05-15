from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.cv import AwardsRequest
from app.utils.response_schemas import success_response, error_response
from app.data_access.postgres.cv.award_repository import AwardRepository
from app.data_access.postgres.cv.header_repository import CVHeaderRepository

class CVAwardService:
    def __init__(self, db: AsyncSession, repo : AwardRepository, header_repo : CVHeaderRepository):
        self.db = db
        self.repo = repo
        self.header_repo = header_repo

    async def create(self, user_id: int, request: AwardsRequest):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(404, "Header not found for this user.")

        award = await self.repo.create({
            **request.dict(exclude={"header_id"}),
            "header_id": header.id
        })

        return success_response(201, {
            "message": "Award created successfully",
            "data": {
                "id": award.id,
                "award": award.award,
                "organization": award.organization,
                "start_date": award.start_date,
                "end_date": award.end_date,
                "header_id": award.header_id
            }
        })

    async def get(self, award_id: int, user_id: int):
        award = await self.repo.get_by_id(award_id)
        if not award:
            return error_response(404, "Award not found")

        header = await self.header_repo.get_by_id(award.header_id)
        if not header or header.user_id != user_id:
            return error_response(403, "Unauthorized access")

        return success_response(200, {
            "award": {
                "id": award.id,
                "award": award.award,
                "organization": award.organization,
                "start_date": award.start_date,
                "end_date": award.end_date,
            }
        })

    async def delete(self, award_id: int, user_id: int):
        award = await self.repo.get_by_id(award_id)
        if not award:
            return error_response(404, "Award not found")

        header = await self.header_repo.get_by_id(award.header_id)
        if not header or header.user_id != user_id:
            return error_response(403, "Unauthorized")

        await self.repo.delete(award)
        return success_response(200, {"message": "Award deleted successfully"})
