from fastapi import APIRouter, Depends
from backend.core.providers.domain_providers.user_provider import get_current_user
from backend.core.providers.domain_providers.cv_providers import get_cv_skills_service
from backend.schemas.cv import SkillsLanguagesRequest, SaveSkillsRequest, GenerateSkillsRequest
from backend.domain_services.cv_services.cv_skill_language_service import CVSkillsService

router = APIRouter()

@router.post("/api/skills-languages/", tags=["Skills & Languages"])
async def create_skills_languages(
    request: SkillsLanguagesRequest,
    user: dict = Depends(get_current_user),
    service: CVSkillsService = Depends(get_cv_skills_service)
):
    return await service.create(request, user["user_id"])


# @router.get("/api/skills-languages/{skills_id}/", tags=["Skills & Languages"])
# async def get_skills_languages(
#     skills_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVSkillsService = Depends(get_cv_skills_service)
# ):
#     return await service.get(skills_id, user["user_id"])


# @router.delete("/api/skills-languages/{skills_id}/", tags=["Skills & Languages"])
# async def delete_skills_languages(
#     skills_id: int,
#     user: dict = Depends(get_current_user),
#     service: CVSkillsService = Depends(get_cv_skills_service)
# ):
#     return await service.delete(skills_id, user["user_id"])


@router.post("/api/skills/suggestions/", tags=["AI Enhancements"])
async def generate_skills_suggestions(
    request: GenerateSkillsRequest,
    user: dict = Depends(get_current_user),
    service: CVSkillsService = Depends(get_cv_skills_service)
):
    return await service.generate_suggestions(user["user_id"])


@router.put("/api/skills/save/{skills_id}/", tags=["AI Enhancements"])
async def save_skills(
    skills_id: int,
    request: SaveSkillsRequest,
    user: dict = Depends(get_current_user),
    service: CVSkillsService = Depends(get_cv_skills_service)
):
    return await service.save(
        skills_id=skills_id,
        user_id=user["user_id"],
        selected_skills=request.selected_skills,
        selected_language=request.selected_language,
        selected_level=request.selected_level
    )
