from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_section_models import Header, Education
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object

class CVEducationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user_header(self, user_id: int):
        result = await self.db.execute(select(Header).where(Header.user_id == user_id))
        return result.scalars().first()

    async def create(self, request, user_id: int):
        header = await self._get_user_header(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        education = Education(**request.dict(exclude={"header_id"}), header_id=header.id)
        self.db.add(education)
        await self.db.commit()
        await self.db.refresh(education)

        return success_response(code=201, data={
            "message": "Education created successfully",
            "education": serialize_sqlalchemy_object(education)
        })

    async def get(self, education_id: int, user_id: int):
        education = await self.db.get(Education, education_id)
        if not education:
            return error_response(code=404, error_message="Education not found")

        header = await self.db.get(Header, education.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this education")

        return success_response(code=200, data={"education": serialize_sqlalchemy_object(education)})

    async def update(self, education_id: int, request, user_id: int):
        education = await self.db.get(Education, education_id)
        if not education:
            return error_response(code=404, error_message="Education not found")

        header = await self.db.get(Header, education.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this education")

        for key, value in request.dict(exclude_unset=True).items():
            setattr(education, key, value)

        await self.db.commit()
        await self.db.refresh(education)

        return success_response(code=200, data={
            "message": "Education updated successfully",
            "education": serialize_sqlalchemy_object(education)
        })

    async def delete(self, education_id: int, user_id: int):
        education = await self.db.get(Education, education_id)
        if not education:
            return error_response(code=404, error_message="Education not found")

        header = await self.db.get(Header, education.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to this education")

        await self.db.delete(education)
        await self.db.commit()

        return success_response(code=200, data={"message": "Education deleted successfully"})
