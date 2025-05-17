from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.response_schemas import success_response, error_response
from backend.data_access.postgres.cv.volunteering_repository import VolunteeringRepository
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService

class CVVolunteeringService:
    def __init__(self, db: AsyncSession, volunteer_repo: VolunteeringRepository, header_repo: CVHeaderRepository, gemini_service: GeminiAIService):
        self.db = db
        self.volunteer_repo = volunteer_repo
        self.header_repo = header_repo
        self.gemini_service = gemini_service

    async def create(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        data = request.dict(exclude={"header_id"})
        data["header_id"] = header.id
        volunteering = await self.volunteer_repo.create(data)

        return success_response(code=201, data=volunteering, message="Volunteering experience created successfully")

    async def get(self, volunteering_id: int, user_id: int):
        volunteering = await self.volunteer_repo.get_by_id(volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await self.header_repo.get_by_id(volunteering.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        return success_response(code=200, data=volunteering)

    async def delete(self, volunteering_id: int, user_id: int):
        volunteering = await self.volunteer_repo.get_by_id(volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await self.header_repo.get_by_id(volunteering.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        await self.volunteer_repo.delete(volunteering)
        return success_response(code=200, data={"message": "Volunteering experience deleted successfully"})

    async def generate_suggestions(self, volunteering_id: int, user_id: int):
        volunteering = await self.volunteer_repo.get_by_id(volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await self.header_repo.get_by_id(volunteering.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        ai_suggestions = await self.gemini_service.generate_volunteering_description(volunteering.role)

        return success_response(code=200, data={
            "message": "AI suggestions generated successfully",
            "suggestions": ai_suggestions
        })

    async def save_description(self, volunteering_id: int, selected_description: str, user_id: int):
        volunteering = await self.volunteer_repo.get_by_id(volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await self.header_repo.get_by_id(volunteering.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        volunteering = await self.volunteer_repo.update_description(volunteering, selected_description)

        return success_response(code=200, data={
            "volunteering_id": volunteering.id,
            "description": volunteering.description
        })
