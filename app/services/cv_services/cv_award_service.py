from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.database.models.cv_section_models import Header, Awards
from app.schemas.cv import AwardsRequest


class CVAwardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user_header(self, user_id: int):
        result = await self.db.execute(select(Header).where(Header.user_id == int(user_id)))
        header = result.scalars().first()
        if not header:
            raise HTTPException(status_code=404, detail="Header not found for this user.")
        return header

    async def create(self, user_id: int, request: AwardsRequest):
        header = await self._get_user_header(user_id)
        award = Awards(**request.dict(exclude={"header_id"}), header_id=header.id)
        self.db.add(award)
        await self.db.commit()
        await self.db.refresh(award)
        return award

    async def get(self, award_id: int, user_id: int):
        award = await self.db.get(Awards, award_id)
        if not award:
            raise HTTPException(status_code=404, detail="Award not found")

        header = await self.db.get(Header, award.header_id)
        if not header or header.user_id != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to access this award.")

        return award

    async def delete(self, award_id: int, user_id: int):
        award = await self.db.get(Awards, award_id)
        if not award:
            raise HTTPException(status_code=404, detail="Award not found")

        header = await self.db.get(Header, award.header_id)
        if not header or header.user_id != user_id:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this award.")

        await self.db.delete(award)
        await self.db.commit()
