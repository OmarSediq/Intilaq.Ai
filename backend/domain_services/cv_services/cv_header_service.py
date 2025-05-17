from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from backend.database.models.cv_models import Header
from backend.schemas.cv import HeaderRequest
from backend.utils.response_schemas import success_response, error_response


class CVHeaderService:
    def __init__(self, db: AsyncSession, header_repo: CVHeaderRepository):
        self.db = db
        self.header_repo = header_repo

    async def create_header(self, request: HeaderRequest, user_id: int):
        try:
            existing_header = await self.header_repo.get_by_user_id(user_id)
            if existing_header:
                return error_response(
                    code=status.HTTP_400_BAD_REQUEST,
                    error_message="Header already exists for this user"
                )

            header = Header(user_id=user_id, **request.dict())
            header = await self.header_repo.create(header)

            return success_response(
                code=status.HTTP_201_CREATED,
                data={
                    "message": "Header created successfully",
                    "header": header
                }
            )
        except Exception as e:
            print(f"[ERROR] Failed to create header: {e}")
            return error_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_message="Internal error while creating header"
            )
