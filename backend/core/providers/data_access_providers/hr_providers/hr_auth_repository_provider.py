# app/core/providers/data_access_providers/hr_repository_provider.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.hr.hr_auth_repository import HRRepository

def get_hr_repository(db: AsyncSession = Depends(get_db)) -> HRRepository:
    return HRRepository(db)
