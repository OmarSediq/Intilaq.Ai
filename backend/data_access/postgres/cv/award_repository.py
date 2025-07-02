from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models.cv_models import Awards

class AwardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, award_id: int):
        return await self.db.get(Awards, award_id)

    async def create(self, data: dict):
        award = Awards(**data)
        self.db.add(award)
        await self.db.commit()
        await self.db.refresh(award)
        return award

    async def delete(self, award: Awards):
        await self.db.delete(award)
        await self.db.commit()
