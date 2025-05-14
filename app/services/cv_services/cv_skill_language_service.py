from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_section_models import Header, SkillsLanguages
from app.utils.response_schemas import success_response, error_response
from app.services.ai_services import generate_skills_from_ai


class CVSkillsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user_header(self, user_id: int):
        result = await self.db.execute(select(Header).where(Header.user_id == user_id))
        return result.scalars().first()

    async def create(self, request, user_id: int):
        header = await self._get_user_header(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        record = SkillsLanguages(
            header_id=header.id,
            skills=request.skills,
            languages=request.languages,
            level=request.level
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        return success_response(code=201, data={
            "id": record.id,
            "header_id": record.header_id,
            "skills": record.skills,
            "languages": record.languages,
            "level": record.level
        }, message="Skills & Languages created successfully")

    async def get(self, skills_id: int, user_id: int):
        skills = await self.db.get(SkillsLanguages, skills_id)
        if not skills:
            return error_response(code=404, error_message="Skills & Languages not found")

        header = await self.db.get(Header, skills.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="You do not have permission to view this resource.")

        return success_response(code=200, data={
            "id": skills.id,
            "header_id": skills.header_id,
            "skills": skills.skills,
            "languages": skills.languages,
            "level": skills.level
        }, message="Skills & Languages retrieved successfully")

    async def delete(self, skills_id: int, user_id: int):
        skills = await self.db.get(SkillsLanguages, skills_id)
        if not skills:
            return error_response(code=404, error_message="Skills & Languages not found")

        header = await self.db.get(Header, skills.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="You do not have permission to delete this resource.")

        await self.db.delete(skills)
        await self.db.commit()

        return success_response(code=200, data={"message": "Skills & Languages deleted successfully"})

    async def generate_suggestions(self, user_id: int):
        header = await self._get_user_header(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        db_skills = SkillsLanguages(header_id=header.id, skills="", languages="", level=None)
        self.db.add(db_skills)
        await self.db.commit()
        await self.db.refresh(db_skills)

        ai_suggestions = await generate_skills_from_ai(
            job_title=header.job_title,
            years_of_experience=header.years_of_experience
        )

        return success_response(code=200, data={
            "skills_languages_id": db_skills.id,
            "suggestions": ai_suggestions
        })

    async def save(self, skills_id: int, user_id: int, selected_skills: str, selected_language: str, selected_level: str):
        skills = await self.db.get(SkillsLanguages, skills_id)
        if not skills:
            return error_response(code=404, error_message="Skills record not found.")

        header = await self.db.get(Header, skills.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this skills record.")

        skills.skills = selected_skills
        skills.languages = selected_language
        skills.level = selected_level

        await self.db.commit()
        await self.db.refresh(skills)

        return success_response(code=200, data={
            "skills": skills.skills,
            "languages": skills.languages,
            "level": skills.level
        })
