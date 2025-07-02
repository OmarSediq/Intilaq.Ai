from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.email_utils import send_email
from backend.utils.response_schemas import success_response, error_response
import random
from backend.data_access.postgres.hr.hr_auth_repository import HRRepository

class HRRegisterService:
    def __init__(self, db: AsyncSession , hr_repo: HRRepository):
        self.db = db
        self.hr_repo = hr_repo

    async def register(self, request):
        if request.password != request.confirm_password:
            return error_response(code=400, error_message="Passwords do not match")

        existing_hr = await self.hr_repo.get_by_email(request.business_email)
        if existing_hr:
            return error_response(code=400, error_message="Email already registered")

        await self.hr_repo.create(request)
        code = str(random.randint(100000, 999999))
        await self.hr_repo.save_reset_code(request.business_email, code)

        send_email(request.business_email, "Verify your HR account", f"Your code is: {code}")
        return success_response(code=201, data={"message": "Account created. Please verify it."})
