from app.data_access.postgres.cv.header_repository import CVHeaderRepository
from app.data_access.postgres.cv.objective_repository import CVObjectiveRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.response_schemas import success_response, error_response
from app.domain_services.ai_services import generate_objective_from_ai

class CVObjectiveService:
    def __init__(self, db: AsyncSession, header_repo: CVHeaderRepository, objective_repo: CVObjectiveRepository):
        self.db = db
        self.header_repo = header_repo
        self.objective_repo = objective_repo

    async def generate_objective_suggestions(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        if not header.job_title or not header.years_of_experience:
            return error_response(code=400, error_message="Missing job title or years of experience in header.")

        objective = await self.objective_repo.create_objective(header_id=header.id, description=request.description or "")

        ai_suggestions = await generate_objective_from_ai(
            job_title=header.job_title,
            years_of_experience=header.years_of_experience
        )

        return success_response(code=200, data={
            "objective_id": objective.id,
            "header_id": header.id,
            "suggestions": ai_suggestions
        })

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

        return success_response(code=200, data={
            "objective_id": updated.id,
            "description": updated.description
        })
