from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_models import Header, SkillsLanguages
from app.utils.response_schemas import success_response, error_response
from app.domain_services.ai_services import generate_skills_from_ai
from app.data_access.postgres.cv.skill_language_repository import SkillsLanguagesRepository
from app.data_access.postgres.cv.header_repository import CVHeaderRepository
class CVSkillsService:
    def __init__(self, db: AsyncSession, skills_repo: SkillsLanguagesRepository, header_repo: CVHeaderRepository):
        self.db = db
        self.skills_repo = skills_repo
        self.header_repo = header_repo

    async def create(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
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
        skills = await self.skills_repo.get_by_id(skills_id)
        if not skills:
            return error_response(code=404, error_message="Skills & Languages not found")

        header = await self.header_repo.get_by_id(skills.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="You do not have permission to view this resource.")

        return success_response(code=200, data={
            "id": skills.id,
            "header_id": skills.header_id,
            "skills": skills.skills,
            "languages": skills.languages,
            "level": skills.level
        })

    async def delete(self, skills_id: int, user_id: int):
        skills = await self.skills_repo.get_by_id(skills_id)
        if not skills:
            return error_response(code=404, error_message="Skills & Languages not found")

        header = await self.header_repo.get_by_id(skills.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access")

        await self.skills_repo.delete(skills)
        return success_response(code=200, data={"message": "Deleted successfully"})

    async def generate_suggestions(self, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        skills = await self.skills_repo.create(header_id=header.id)

        ai_suggestions = await generate_skills_from_ai(
            job_title=header.job_title,
            years_of_experience=header.years_of_experience
        )

        return success_response(code=200, data={
            "skills_languages_id": skills.id,
            "suggestions": ai_suggestions
        })

    async def save(self, skills_id: int, user_id: int, selected_skills: str, selected_language: str, selected_level: str):
        skills = await self.skills_repo.get_by_id(skills_id)
        if not skills:
            return error_response(code=404, error_message="Skills record not found.")

        header = await self.header_repo.get_by_id(skills.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this record.")

        updated = await self.skills_repo.update(skills, {
            "skills": selected_skills,
            "languages": selected_language,
            "level": selected_level
        })

        return success_response(code=200, data={
            "skills": updated.skills,
            "languages": updated.languages,
            "level": updated.level
        })
