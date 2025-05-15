from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_models import Header

class CVHeaderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int):
        result = await self.db.execute(select(Header).where(Header.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, header_id: int):
        return await self.db.get(Header, header_id)

    async def create(self, header: Header):
        self.db.add(header)
        await self.db.commit()
        await self.db.refresh(header)
        return header

    async def delete(self, header: Header):
        await self.db.delete(header)
        await self.db.commit()

    async def get_header_id_by_user_id(self, user_id: int) -> int | None:
        stmt = select(Header.id).where(Header.user_id == int(user_id))
        result = await self.db.execute(stmt)
        return result.scalar()
