from backend.data_access.postgres.cv.education_repository import EducationRepository
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.utils.response_schemas import success_response, error_response
from sqlalchemy.ext.asyncio import AsyncSession

class CVEducationService:
    def __init__(self, db: AsyncSession, header_repo: CVHeaderRepository, education_repo: EducationRepository):
        self.db = db
        self.header_repo = header_repo
        self.education_repo = education_repo

    async def create(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        education = await self.education_repo.create({
            **request.dict(exclude={"header_id"}),
            "header_id": header.id
        })

        return success_response(code=201, data={
            "message": "Education created successfully",
            "education": education
        })

    async def get(self, education_id: int, user_id: int):
        education = await self.education_repo.get_by_id(education_id)
        if not education:
            return error_response(code=404, error_message="Education not found")

        header = await self.header_repo.get_by_id(education.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this education")

        return success_response(code=200, data={"education": education})

    async def update(self, education_id: int, request, user_id: int):
        education = await self.education_repo.get_by_id(education_id)
        if not education:
            return error_response(code=404, error_message="Education not found")

        header = await self.header_repo.get_by_id(education.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this education")

        updated = await self.education_repo.update(education, request.dict(exclude_unset=True))

        return success_response(code=200, data={
            "message": "Education updated successfully",
            "education": updated
        })

    async def delete(self, education_id: int, user_id: int):
        education = await self.education_repo.get_by_id(education_id)
        if not education:
            return error_response(code=404, error_message="Education not found")

        header = await self.header_repo.get_by_id(education.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this education")

        await self.education_repo.delete(education)

        return success_response(code=200, data={"message": "Education deleted successfully"})
