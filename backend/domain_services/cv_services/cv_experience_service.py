from backend.data_access.postgres.cv.experience_repository import ExperienceRepository
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.schemas.cv_schema import ExperienceResponse
from backend.utils.response_schemas import success_response, error_response
from sqlalchemy.ext.asyncio import AsyncSession
from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService

class CVExperienceService:
    def __init__(self, db: AsyncSession, header_repo: CVHeaderRepository, experience_repo: ExperienceRepository, gemini_service: GeminiAIService):
        self.db = db
        self.header_repo = header_repo
        self.experience_repo = experience_repo
        self.gemini_service = gemini_service

    async def create(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")


        experience = await self.experience_repo.create({
            **request.model_dump(exclude={"header_id"}),
            "header_id": header.id
        })

        response_data = ExperienceResponse.model_validate(experience)

        return success_response(code=201, data={
            "message": "Experience created successfully",
            "experience": response_data.model_dump()
        })

    async def generate_suggestions(self, user_id: int, experience_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        experience = await self.experience_repo.get_by_id(experience_id)
        if not experience or experience.header_id != header.id:
            return error_response(code=403, error_message="Unauthorized access to this experience.")

        ai_suggestions = await self.gemini_service.generate_experience(
            role=experience.role,
            company_name=experience.company_name,
            start_date=experience.start_date,
            end_date=experience.end_date
        )

        return success_response(code=200, data={
            "experience_id": experience.id,
            "role": experience.role,
            "suggestions": ai_suggestions
        })

    async def save_description(self, experience_id: int, description: str, user_id: int):
        experience = await self.experience_repo.get_by_id(experience_id)
        if not experience:
            return error_response(code=404, error_message="Experience not found.")

        header = await self.header_repo.get_by_user_id(user_id)
        if not header or experience.header_id != header.id:
            return error_response(code=403, error_message="Unauthorized access to this experience.")

        updated = await self.experience_repo.update(experience, {"description": description})

        return success_response(code=200, data={
            "experience_id": updated.id,
            "description": updated.description
        })
