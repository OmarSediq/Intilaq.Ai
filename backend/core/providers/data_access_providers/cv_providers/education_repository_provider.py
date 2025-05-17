from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.cv.education_repository import EducationRepository

def get_education_repository(db: AsyncSession = Depends(get_db)) -> EducationRepository:
    return EducationRepository(db)
