from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

class HRUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_company_field_by_hr_id(self, hr_id: int) -> str:
        query = text("SELECT company_field FROM hr.hr_users WHERE id = :hr_id")
        result = await self.db.execute(query, {"hr_id": hr_id})
        return result.scalar_one_or_none() or "your company"
