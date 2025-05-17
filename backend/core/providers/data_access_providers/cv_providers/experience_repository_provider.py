from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.cv.experience_repository import ExperienceRepository

def get_experience_repository(db: AsyncSession = Depends(get_db)) -> ExperienceRepository:
    return ExperienceRepository(db)
