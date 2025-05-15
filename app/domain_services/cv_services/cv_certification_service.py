from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.data_access.postgres.cv.certification_repository import CertificationRepository
from app.data_access.postgres.cv.header_repository import CVHeaderRepository

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

        return success_response(code=201, data={
            "message": "Certification created successfully",
            "data": serialize_sqlalchemy_object(cert)
        })

    async def get(self, certification_id: int, user_id: int):
        cert = await self.cert_repo.get_by_id(certification_id)
        if not cert:
            return error_response(code=404, error_message="Certification not found")

        header = await self.header_repo.get_by_id(cert.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        return success_response(code=200, data={"data": serialize_sqlalchemy_object(cert)})

    async def update(self, certification_id: int, request, user_id: int):
        cert = await self.cert_repo.get_by_id(certification_id)
        if not cert:
            return error_response(code=404, error_message="Certification not found")

        header = await self.header_repo.get_by_id(cert.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        update_data = request.dict(exclude_unset=True)
        if "link" in update_data and update_data["link"] is not None:
            update_data["link"] = str(update_data["link"])

        cert = await self.cert_repo.update(cert, update_data)

        return success_response(code=200, data={
            "message": "Certification updated successfully",
            "data": serialize_sqlalchemy_object(cert)
        })

    async def delete(self, certification_id: int, user_id: int):
        cert = await self.cert_repo.get_by_id(certification_id)
        if not cert:
            return error_response(code=404, error_message="Certification not found")

        header = await self.header_repo.get_by_id(cert.header_id)
        if not header or header.user_id != user_id:
            return error_response(code=403, error_message="Unauthorized")

        await self.cert_repo.delete(cert)

        return success_response(code=200, data={"message": "Certification deleted successfully"})
