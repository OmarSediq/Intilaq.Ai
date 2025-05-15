from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_models import Experience

class ExperienceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Experience:
        experience = Experience(**data)
        self.db.add(experience)
        await self.db.commit()
        await self.db.refresh(experience)
        return experience

    async def get_by_id(self, experience_id: int) -> Experience | None:
        result = await self.db.execute(select(Experience).where(Experience.id == experience_id))
        return result.scalars().first()

    async def update(self, experience: Experience, data: dict) -> Experience:
        for key, value in data.items():
            setattr(experience, key, value)
        await self.db.commit()
        await self.db.refresh(experience)
        return experience

    async def delete(self, experience: Experience):
        await self.db.delete(experience)
        await self.db.commit()

    async def get_by_header_id(self, header_id: int) -> Experience | None:
        result = await self.db.execute(select(Experience).where(Experience.header_id == header_id))
        return result.scalars().first()
