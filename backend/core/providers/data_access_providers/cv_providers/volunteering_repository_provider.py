from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.cv.volunteering_repository import VolunteeringRepository

def get_volunteering_repository(
    db: AsyncSession = Depends(get_db)
) -> VolunteeringRepository:
    return VolunteeringRepository(db)
