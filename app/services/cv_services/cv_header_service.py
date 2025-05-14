from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status
from app.database.models.cv_section_models import Header
from app.schemas.cv import HeaderRequest
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object

class CVHeaderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_header(self, request: HeaderRequest, user_id: int):
        try:
            result = await self.db.execute(select(Header).where(Header.user_id == user_id))
            existing_header = result.scalar_one_or_none()
            if existing_header:
                return error_response(
                    code=status.HTTP_400_BAD_REQUEST,
                    error_message="Header already exists for this user"
                )

            header = Header(user_id=user_id, **request.dict())
            self.db.add(header)
            await self.db.commit()
            await self.db.refresh(header)

            return success_response(
                code=status.HTTP_201_CREATED,
                data={
                    "message": "Header created successfully",
                    "header": serialize_sqlalchemy_object(header)
                }
            )
        except Exception as e:
            print(f"[ERROR] Failed to create header: {e}")
            return error_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_message="Internal error while creating header"
            )

    async def get_header(self, header_id: int, user_id: int):
        header = await self.db.get(Header, header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to header")

        return success_response(code=200, data={"header": serialize_sqlalchemy_object(header)})

    async def update_header(self, header_id: int, request: HeaderRequest, user_id: int):
        header = await self.db.get(Header, header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to header")

        for key, value in request.dict(exclude_unset=True).items():
            setattr(header, key, value)

        await self.db.commit()
        await self.db.refresh(header)

        return success_response(code=200, data={
            "message": "Header updated successfully",
            "header": serialize_sqlalchemy_object(header)
        })

    async def delete_header(self, header_id: int, user_id: int):
        header = await self.db.get(Header, header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized access to header")

        await self.db.delete(header)
        await self.db.commit()

        return success_response(code=200, data={"message": "Header deleted successfully"})
