from app.data_access.postgres.cv.experience_repository import ExperienceRepository
from app.data_access.postgres.cv.header_repository import CVHeaderRepository
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.domain_services.ai_services import generate_experience_from_ai
from sqlalchemy.ext.asyncio import AsyncSession

class CVExperienceService:
    def __init__(self, db: AsyncSession, header_repo: CVHeaderRepository, experience_repo: ExperienceRepository):
        self.db = db
        self.header_repo = header_repo
        self.experience_repo = experience_repo

    async def create(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        request.validate_dates(request.start_date, request.end_date)

        experience = await self.experience_repo.create({
            **request.dict(exclude={"header_id"}),
            "header_id": header.id
        })

        return success_response(code=201, data={
            "message": "Experience created successfully",
            "experience": serialize_sqlalchemy_object(experience)
        })

    async def get(self, experience_id: int, user_id: int):
        experience = await self.experience_repo.get_by_id(experience_id)
        if not experience:
            return error_response(code=404, error_message="Experience not found")

        header = await self.header_repo.get_by_id(experience.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this experience")

        return success_response(code=200, data={"experience": serialize_sqlalchemy_object(experience)})

    async def update(self, experience_id: int, request, user_id: int):
        experience = await self.experience_repo.get_by_id(experience_id)
        if not experience:
            return error_response(code=404, error_message="Experience not found")

        header = await self.header_repo.get_by_id(experience.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this experience")

        request.validate_dates(request.start_date, request.end_date)

        updated = await self.experience_repo.update(experience, request.dict(exclude_unset=True))

        return success_response(code=200, data={
            "message": "Experience updated successfully",
            "experience": serialize_sqlalchemy_object(updated)
        })

    async def delete(self, experience_id: int, user_id: int):
        experience = await self.experience_repo.get_by_id(experience_id)
        if not experience:
            return error_response(code=404, error_message="Experience not found")

        header = await self.header_repo.get_by_id(experience.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this experience")

        await self.experience_repo.delete(experience)

        return success_response(code=200, data={"message": "Experience deleted successfully"})

    async def generate_suggestions(self, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        experience = await self.experience_repo.get_by_header_id(header.id)
        if not experience:
            return error_response(code=404, error_message="Experience not found for this user.")

        ai_suggestions = await generate_experience_from_ai(
            role=experience.role,
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
