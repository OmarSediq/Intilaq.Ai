from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.cv.award_repository import AwardRepository

def get_award_repository(db: AsyncSession = Depends(get_db)) -> AwardRepository:
    return AwardRepository(db)
