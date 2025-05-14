from sqlalchemy.ext.asyncio import AsyncSession
from app.services.db_services import get_hr_by_email, create_hr_user, save_hr_reset_code
from app.utils.email_utils import send_email
from app.utils.response_schemas import success_response, error_response
import random

class HRRegisterService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, request):
        if request.password != request.confirm_password:
            return error_response(code=400, error_message="Passwords do not match")

        existing_hr = await get_hr_by_email(request.business_email, self.db)
        if existing_hr:
            return error_response(code=400, error_message="Email already registered")

        await create_hr_user(request, self.db)
        code = str(random.randint(100000, 999999))
        await save_hr_reset_code(request.business_email, code, self.db)

        send_email(request.business_email, "Verify your HR account", f"Your code is: {code}")
        return success_response(code=201, data={"message": "Account created. Please verify it."})
