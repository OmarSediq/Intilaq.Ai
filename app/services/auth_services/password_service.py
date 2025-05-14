import random, asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.db_services import get_user_by_email, save_reset_code
from app.utils.response_schemas import success_response, error_response
from app.utils.email_utils import send_email

class PasswordRecoveryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def forgot_password(self, request):
        user = await get_user_by_email(request.email, self.db)
        if not user:
            return error_response(code=404, error_message="Email not found")

        code = str(random.randint(100000, 999999))
        await save_reset_code(request.email, code, self.db)

        try:
            await asyncio.get_event_loop().run_in_executor(
                None, send_email, request.email, "Reset Password", f"Code: {code}"
            )
        except Exception as e:
            return error_response(code=500, error_message=f"Email error: {str(e)}")

        return success_response(code=200, data={"message": "Reset code sent"})
