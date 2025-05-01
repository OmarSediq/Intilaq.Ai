from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Header, SkillsLanguages
from app.utils.response_schemas import success_response, error_response
from app.services.ai_services import generate_skills_from_ai


async def create_skills_languages_service(request, user_id: int, db: AsyncSession):
    user_id = int(user_id)
    result = await db.execute(select(Header).where(Header.user_id == user_id))
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


async def get_skills_languages_service(skills_id: int, user_id: int, db: AsyncSession):
    user_id = int(user_id)
    skills = await db.get(SkillsLanguages, skills_id)
    if not skills:
        return error_response(code=404, error_message="Skills & Languages not found")

    header = await db.get(Header, skills.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="You do not have permission to view this resource.")

    return success_response(code=200, data={
        "id": skills.id,
        "header_id": skills.header_id,
        "skills": skills.skills,
        "languages": skills.languages,
        "level": skills.level
    }, message="Skills & Languages retrieved successfully")


async def delete_skills_languages_service(skills_id: int, user_id: int, db: AsyncSession):
    user_id = int(user_id)
    skills = await db.get(SkillsLanguages, skills_id)
    if not skills:
        return error_response(code=404, error_message="Skills & Languages not found")

    header = await db.get(Header, skills.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="You do not have permission to delete this resource.")

    await db.delete(skills)
    await db.commit()

    return success_response(code=200, data={"message": "Skills & Languages deleted successfully"})


async def generate_skills_suggestions_service(user_id: int, db: AsyncSession):
    user_id = int(user_id)
    result = await db.execute(select(Header).where(Header.user_id == user_id))
    header = result.scalars().first()

    if not header:
        return error_response(code=404, error_message="Header not found for this user.")

    db_skills = SkillsLanguages(header_id=header.id, skills="", languages="", level=None)
    db.add(db_skills)
    await db.commit()
    await db.refresh(db_skills)

    ai_suggestions = await generate_skills_from_ai(
        job_title=header.job_title,
        years_of_experience=header.years_of_experience
    )

    return success_response(code=200, data={
        "skills_languages_id": db_skills.id,
        "suggestions": ai_suggestions
    })


async def save_skills_service(skills_id: int, user_id: int, selected_skills: str, selected_language: str, selected_level: str, db: AsyncSession):
    user_id = int(user_id)
    skills = await db.get(SkillsLanguages, skills_id)
    if not skills:
        return error_response(code=404, error_message="Skills record not found.")

    header = await db.get(Header, skills.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized access to this skills record.")

    skills.skills = selected_skills
    skills.languages = selected_language
    skills.level = selected_level

    await db.commit()
    await db.refresh(skills)

    return success_response(code=200, data={
        "skills": skills.skills,
        "languages": skills.languages,
        "level": skills.level
    })
