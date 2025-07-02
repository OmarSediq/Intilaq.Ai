from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.cv.objective_repository import CVObjectiveRepository

def get_objective_repository(db: AsyncSession = Depends(get_db)) -> CVObjectiveRepository:
    return CVObjectiveRepository(db)
