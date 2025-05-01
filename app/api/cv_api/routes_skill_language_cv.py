from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.schemas.cv import SkillsLanguagesRequest, SaveSkillsRequest, GenerateSkillsRequest
from app.services.cv_services.skill_language_services import (
    create_skills_languages_service,
    get_skills_languages_service,
    delete_skills_languages_service,
    generate_skills_suggestions_service,
    save_skills_service
)

router = APIRouter()


@router.post("/api/skills-languages/", tags=["Skills & Languages"])
async def create_skills_languages(
    request: SkillsLanguagesRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_skills_languages_service(request, user_id=user["user_id"], db=db)


@router.get("/api/skills-languages/{skills_id}/", tags=["Skills & Languages"])
async def get_skills_languages(
    skills_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_skills_languages_service(skills_id, user_id=user["user_id"], db=db)


@router.delete("/api/skills-languages/{skills_id}/", tags=["Skills & Languages"])
async def delete_skills_languages(
    skills_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await delete_skills_languages_service(skills_id, user_id=user["user_id"], db=db)


@router.post("/api/skills/suggestions/", tags=["AI Enhancements"])
async def generate_skills_suggestions(
    request: GenerateSkillsRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await generate_skills_suggestions_service(user_id=user["user_id"], db=db)


@router.put("/api/skills/save/{skills_id}/", tags=["AI Enhancements"])
async def save_skills(
    skills_id: int,
    request: SaveSkillsRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await save_skills_service(
        skills_id=skills_id,
        user_id=user["user_id"],
        selected_skills=request.selected_skills,
        selected_language=request.selected_language,
        selected_level=request.selected_level,
        db=db
    )
