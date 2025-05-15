from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.providers.infra_providers import get_db
from app.data_access.postgres.user_repository import UserRepository

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


