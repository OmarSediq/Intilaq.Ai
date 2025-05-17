from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.hr.hr_user_repository import HRUserRepository

async def get_hr_user_repository(db: AsyncSession = Depends(get_db)) -> HRUserRepository:
    return HRUserRepository(db)
