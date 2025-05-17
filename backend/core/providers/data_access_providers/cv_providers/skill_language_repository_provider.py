from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.data_access.postgres.cv.skill_language_repository import SkillsLanguagesRepository

def get_skills_languages_repository(
    db: AsyncSession = Depends(get_db)
) -> SkillsLanguagesRepository:
    return SkillsLanguagesRepository(db)
