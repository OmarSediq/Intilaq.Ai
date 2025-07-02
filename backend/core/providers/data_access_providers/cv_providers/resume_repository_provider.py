from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.cv.resume_repository import ResumeRepository

def get_resume_repository(db: AsyncSession = Depends(get_db)) -> ResumeRepository:
    return ResumeRepository(db)
