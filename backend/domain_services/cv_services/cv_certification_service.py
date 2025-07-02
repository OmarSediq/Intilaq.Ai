from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.cv_schema import CertResponse
from backend.utils.response_schemas import success_response, error_response
from backend.data_access.postgres.cv.certification_repository import CertificationRepository
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository

class CVCertificationService:
    def __init__(self, db: AsyncSession, cert_repo: CertificationRepository, header_repo: CVHeaderRepository):
        self.db = db
        self.cert_repo = cert_repo
        self.header_repo = header_repo

    async def create(self, request, user_id: int):
        header = await self.header_repo.get_by_user_id(user_id)
        if not header:
            return error_response(code=404, error_message="Header not found")

        data = request.dict(exclude={"header_id"})
        data["header_id"] = header.id
        cert = await self.cert_repo.create(data)

        return success_response(code=201, data=CertResponse.model_validate(cert).model_dump())

