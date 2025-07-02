from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository

def get_header_repository(db: AsyncSession = Depends(get_db)) -> CVHeaderRepository:
    return CVHeaderRepository(db)
