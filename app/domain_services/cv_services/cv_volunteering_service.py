from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.domain_services.ai_services import generate_volunteering_description_from_ai
from app.data_access.postgres.cv.volunteering_repository import VolunteeringRepository
from app.data_access.postgres.cv.header_repository import CVHeaderRepository

class CVVolunteeringService:
    def __init__(self, db: AsyncSession, repo: VolunteeringRepository, header_repo: CVHeaderRepository):
        self.db = db
        self.repo = repo
        self.header_repo = header_repo

    async def create(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        data = request.dict(exclude={"header_id"})
        data["header_id"] = header.id
        volunteering = await self.repo.create(data)

        return success_response(code=201, data={
            "message": "Volunteering experience created successfully",
            "data": serialize_sqlalchemy_object(volunteering)
        })

    async def get(self, volunteering_id: int, user_id: int):
        volunteering = await self.repo.get_by_id(volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await self.header_repo.get_by_id(volunteering.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        return success_response(code=200, data={"data": serialize_sqlalchemy_object(volunteering)})

    async def delete(self, volunteering_id: int, user_id: int):
        volunteering = await self.repo.get_by_id(volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await self.header_repo.get_by_id(volunteering.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        await self.repo.delete(volunteering)
        return success_response(code=200, data={"message": "Volunteering experience deleted successfully"})

    async def generate_suggestions(self, volunteering_id: int, user_id: int):
        volunteering = await self.repo.get_by_id(volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await self.header_repo.get_by_id(volunteering.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        ai_suggestions = await generate_volunteering_description_from_ai(volunteering.role)

        return success_response(code=200, data={
            "message": "AI suggestions generated successfully",
            "suggestions": serialize_sqlalchemy_object(ai_suggestions)
        })

    async def save_description(self, volunteering_id: int, selected_description: str, user_id: int):
        volunteering = await self.repo.get_by_id(volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await self.header_repo.get_by_id(volunteering.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        volunteering = await self.repo.update_description(volunteering, selected_description)

        return success_response(code=200, data={
            "message": "Volunteering description updated successfully",
            "description": volunteering.description
        })
