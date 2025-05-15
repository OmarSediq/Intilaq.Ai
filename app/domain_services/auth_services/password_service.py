import random, asyncio
from app.data_access.postgres.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.response_schemas import success_response, error_response
from app.utils.email_utils import send_email

class PasswordRecoveryService:
    def __init__(self, db: AsyncSession , user_repo : UserRepository):
        self.db = db
        self.user_repo =user_repo

    async def forgot_password(self, request):
        user = await self.user_repo.get_user_by_email(request.email)
        if not user:
            return error_response(code=404, error_message="Email not found")

        code = str(random.randint(100000, 999999))
        await self.user_repo.save_reset_code(request.email, code)

        try:
            await asyncio.get_event_loop().run_in_executor(
                None, send_email, request.email, "Reset Password", f"Code: {code}"
            )
        except Exception as e:
            return error_response(code=500, error_message=f"Email error: {str(e)}")

        return success_response(code=200, data={"message": "Reset code sent"})
