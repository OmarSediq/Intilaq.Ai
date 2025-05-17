from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models.cv_models import VolunteeringExperience

class VolunteeringRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, volunteering_id: int):
        return await self.db.get(VolunteeringExperience, volunteering_id)

    async def create(self, data: dict):
        volunteering = VolunteeringExperience(**data)
        self.db.add(volunteering)
        await self.db.commit()
        await self.db.refresh(volunteering)
        return volunteering

    async def update_description(self, volunteering: VolunteeringExperience, description: str):
        volunteering.description = description
        await self.db.commit()
        await self.db.refresh(volunteering)
        return volunteering

    async def delete(self, volunteering: VolunteeringExperience):
        await self.db.delete(volunteering)
        await self.db.commit()
