from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.database.models import Header, SkillsLanguages
from app.schemas.cv import SkillsLanguagesRequest, SaveSkillsRequest, GenerateSkillsRequest
from app.utils.response_schemas import success_response, error_response
from app.services.ai_services import generate_skills_from_ai

router = APIRouter()


@router.post("/api/skills-languages/", tags=["Skills & Languages"])
async def create_skills_languages(
    request: SkillsLanguagesRequest, 
    user: dict = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()

        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        skills_languages = SkillsLanguages(
            header_id=header.id,
            skills=request.skills,
            languages=request.languages,
            level=request.level
        )
        db.add(skills_languages)
        await db.commit()
        await db.refresh(skills_languages)

        return success_response(code=201, data={
            "id": skills_languages.id,
            "header_id": skills_languages.header_id,
            "skills": skills_languages.skills,
            "languages": skills_languages.languages,
            "level": skills_languages.level
        }, message="Skills & Languages created successfully")

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.get("/api/skills-languages/{skills_id}/", tags=["Skills & Languages"])
async def get_skills_languages(
    skills_id: int, 
    user: dict = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)
):
    try:
        skills_languages = await db.get(SkillsLanguages, skills_id)
        if not skills_languages:
            return error_response(code=404, error_message="Skills & Languages not found")
        
        header = await db.get(Header, skills_languages.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to view this resource.")

        return success_response(code=200, data={
            "id": skills_languages.id,
            "header_id": skills_languages.header_id,
            "skills": skills_languages.skills,
            "languages": skills_languages.languages,
            "level": skills_languages.level
        }, message="Skills & Languages retrieved successfully")

    except Exception as e:
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.delete("/api/skills-languages/{skills_id}/", tags=["Skills & Languages"])
async def delete_skills_languages(
    skills_id: int, 
    user: dict = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)
):
    try:
        skills_languages = await db.get(SkillsLanguages, skills_id)
        if not skills_languages:
            return error_response(code=404, error_message="Skills & Languages not found")
        
        header = await db.get(Header, skills_languages.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to delete this resource.")

        await db.delete(skills_languages)
        await db.commit()
        return success_response(code=200, data={"message": "Skills & Languages deleted successfully"})

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.post("/api/skills/suggestions/", tags=["AI Enhancements"])
async def generate_skills_suggestions(
    request: GenerateSkillsRequest, 
    user: dict = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()

        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        db_skills_languages = SkillsLanguages(
            header_id=header.id,
            skills="",  
            languages="",
            level=None  
        )
        db.add(db_skills_languages)
        await db.commit()
        await db.refresh(db_skills_languages)

        ai_suggestions = await generate_skills_from_ai(
            job_title=header.job_title,
            years_of_experience=header.years_of_experience
        )

        return success_response(code=200, data={
            "skills_languages_id": db_skills_languages.id,
            "suggestions": ai_suggestions
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.put("/api/skills/save/{skills_id}/", tags=["AI Enhancements"])
async def save_skills(
    skills_id: int, 
    request: SaveSkillsRequest, 
    user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    try:
        skills_record = await db.get(SkillsLanguages, skills_id)
        if not skills_record:
            return error_response(code=404, error_message="Skills record not found.")

        header = await db.get(Header, skills_record.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="Unauthorized access to this skills record.")

        skills_record.skills = request.selected_skills
        skills_record.languages = request.selected_language  
        skills_record.level = request.selected_level  

        await db.commit()
        await db.refresh(skills_record) 

        return success_response(code=200, data={
            "skills": skills_record.skills,
            "languages": skills_record.languages,
            "level": skills_record.level
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Error updating skills", data=str(e))
