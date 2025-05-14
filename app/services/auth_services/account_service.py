import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.db_services import (
    create_user, get_user_by_username, save_reset_code,
    update_verification_status, get_user_by_email, get_email_by_code,
    verify_reset_code
)
from app.utils.response_schemas import success_response, error_response
from app.utils.email_utils import send_email
from app.utils.password_utils import get_password_hash

class AccountService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def signup(self, request):
        if request.password != request.confirm_password:
            return error_response(code=400, error_message="Passwords do not match")

        if await get_user_by_username(request.username, self.db):
            return error_response(code=400, error_message="Username already exists")

        await create_user(request.username, request.password, request.email, self.db)
        code = str(random.randint(100000, 999999))
        await save_reset_code(request.email, code, self.db)
        send_email(request.email, "Verify Your Account", f"Your verification code is: {code}")
        return success_response(code=201, data={"message": "Account created. Please verify."})

    async def verify_account(self, request):
        email = await get_email_by_code(request.code, self.db)
        if not email or not await verify_reset_code(email, request.code, self.db):
            return error_response(code=400, error_message="Invalid or expired code")

        user = await get_user_by_email(email, self.db)
        if not user:
            return error_response(code=404, error_message="User not found")

        if request.new_password:
            user.hashed_password = get_password_hash(request.new_password)
            await self.db.commit()
            await self.db.refresh(user)
            return success_response(code=200, data={"message": "Password reset successful"})

        await update_verification_status(email, self.db)
        return success_response(code=200, data={"message": "Verification successful"})

    async def resend_verification_code(self, request):
        user = await get_user_by_email(request.email, self.db)
        if not user:
            return error_response(code=404, error_message="User not found")
        if user.is_verified:
            return error_response(code=400, error_message="Account already verified")

        code = str(random.randint(100000, 999999))
        await save_reset_code(request.email, code, self.db)
        send_email(user.email, "Resend Code", f"Code: {code}")
        return success_response(code=200, data={"message": "Verification code resent"})
