from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.cv_models import SkillsLanguages

class SkillsLanguagesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, header_id: int) -> SkillsLanguages:
        record = SkillsLanguages(header_id=header_id, skills="", languages="", level=None)
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_by_id(self, skills_id: int) -> SkillsLanguages | None:
        return await self.db.get(SkillsLanguages, skills_id)

    async def delete(self, skills: SkillsLanguages):
        await self.db.delete(skills)
        await self.db.commit()

    async def update(self, skills: SkillsLanguages, data: dict) -> SkillsLanguages:
        for key, value in data.items():
            setattr(skills, key, value)
        await self.db.commit()
        await self.db.refresh(skills)
        return skills
