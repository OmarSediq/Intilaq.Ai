from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.data_access.postgres.cv.objective_repository import CVObjectiveRepository
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.cv_schema import ObjectiveResponse
from backend.utils.response_schemas import success_response, error_response
from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService

class CVObjectiveService:
    def __init__(self, db: AsyncSession, header_repo: CVHeaderRepository, objective_repo: CVObjectiveRepository, gemini_service: GeminiAIService):
        self.db = db
        self.header_repo = header_repo
        self.objective_repo = objective_repo
        self.gemini_service = gemini_service

    async def generate_objective_suggestions(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        if not header.job_title or not header.years_of_experience:
            return error_response(code=400, error_message="Missing job title or years of experience in header.")

        objective = await self.objective_repo.create_objective(header_id=header.id,
                                                               description=request.description or "")

        ai_suggestions = await self.gemini_service.generate_objective(
            job_title=header.job_title,
            years_of_experience=header.years_of_experience
        )

        objective_data = ObjectiveResponse.model_validate(objective)

        return success_response(
            code=200,
            data={
                "message": "Suggestions generated successfully",
                "objective": objective_data.model_dump(),
                "suggestions": ai_suggestions
            }
        )

    async def save_objective_description(self, objective_id: int, description: str, user_id: int):
        objective = await self.objective_repo.get_by_id(objective_id)
        if not objective:
            return error_response(code=404, error_message="Objective not found.")

        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        if objective.header_id != header.id:
            return error_response(code=403, error_message="Unauthorized access to this objective.")

        updated = await self.objective_repo.update_description(objective, description)

        response_data = ObjectiveResponse.model_validate(updated)

        return success_response(code=200, data={
            "message": "Objective updated successfully",
            "objective": response_data.model_dump()
        })