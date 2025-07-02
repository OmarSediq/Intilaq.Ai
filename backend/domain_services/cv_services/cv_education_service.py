from backend.data_access.postgres.cv.education_repository import EducationRepository
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.schemas.cv_schema import EducationResponse , EducationRequest
from backend.utils.response_schemas import success_response, error_response
from sqlalchemy.ext.asyncio import AsyncSession

class CVEducationService:
    def __init__(self, db: AsyncSession, header_repo: CVHeaderRepository, education_repo: EducationRepository):
        self.db = db
        self.header_repo = header_repo
        self.education_repo = education_repo

    async def create(self, request: EducationRequest, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        education = await self.education_repo.create({
            **request.model_dump(exclude={"header_id"}),
            "header_id": header.id
        })

        response_data = EducationResponse.model_validate(education).model_dump()

        return success_response(code=201, data={
            "message": "Education created successfully",
            "education": response_data
        })
