from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_section_models import Header, Certifications
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object


class CVCertificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user_header(self, user_id: int):
        result = await self.db.execute(select(Header).where(Header.user_id == user_id))
        return result.scalars().first()

    async def create(self, request, user_id: int):
        header = await self._get_user_header(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        certification = Certifications(
            **request.dict(exclude={"header_id"}),
            header_id=header.id
        )

        self.db.add(certification)
        await self.db.commit()
        await self.db.refresh(certification)

        return success_response(
            code=201,
            data={
                "message": "Certification created successfully",
                "data": serialize_sqlalchemy_object(certification)
            }
        )

    async def get(self, certification_id: int, user_id: int):
        certification = await self.db.get(Certifications, certification_id)
        if not certification:
            return error_response(code=404, error_message="Certification not found")

        header = await self.db.get(Header, certification.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        return success_response(code=200, data={"data": serialize_sqlalchemy_object(certification)})

    async def update(self, certification_id: int, request, user_id: int):
        certification = await self.db.get(Certifications, certification_id)
        if not certification:
            return error_response(code=404, error_message="Certification not found")

        header = await self.db.get(Header, certification.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        update_data = request.dict(exclude_unset=True)
        if "link" in update_data and update_data["link"] is not None:
            update_data["link"] = str(update_data["link"])

        for key, value in update_data.items():
            setattr(certification, key, value)

        await self.db.commit()
        await self.db.refresh(certification)

        return success_response(code=200, data={
            "message": "Certification updated successfully",
            "data": serialize_sqlalchemy_object(certification)
        })

    async def delete(self, certification_id: int, user_id: int):
        certification = await self.db.get(Certifications, certification_id)
        if not certification:
            return error_response(code=404, error_message="Certification not found")

        header = await self.db.get(Header, certification.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        await self.db.delete(certification)
        await self.db.commit()

        return success_response(code=200, data={"message": "Certification deleted successfully"})
