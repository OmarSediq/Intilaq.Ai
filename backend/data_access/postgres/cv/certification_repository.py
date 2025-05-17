from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models.cv_models import Certifications

class CertificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, certification_id: int):
        return await self.db.get(Certifications, certification_id)

    async def create(self, data: dict):
        certification = Certifications(**data)
        self.db.add(certification)
        await self.db.commit()
        await self.db.refresh(certification)
        return certification

    async def update(self, certification: Certifications, update_data: dict):
        for key, value in update_data.items():
            setattr(certification, key, value)
        await self.db.commit()
        await self.db.refresh(certification)
        return certification

    async def delete(self, certification: Certifications):
        await self.db.delete(certification)
        await self.db.commit()
