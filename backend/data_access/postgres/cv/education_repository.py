from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.models.cv_models import Education

class EducationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Education:
        education = Education(**data)
        self.db.add(education)
        await self.db.commit()
        await self.db.refresh(education)
        return education

    async def get_by_id(self, education_id: int) -> Education | None:
        return await self.db.get(Education, education_id)

    async def update(self, education: Education, data: dict) -> Education:
        for key, value in data.items():
            setattr(education, key, value)
        await self.db.commit()
        await self.db.refresh(education)
        return education

    async def delete(self, education: Education):
        await self.db.delete(education)
        await self.db.commit()
