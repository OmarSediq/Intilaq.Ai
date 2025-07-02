from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.cv.certification_repository import CertificationRepository

def get_certification_repository(db: AsyncSession = Depends(get_db)) -> CertificationRepository:
    return CertificationRepository(db)
