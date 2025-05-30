import random
from backend.data_access.postgres.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.response_schemas import success_response, error_response
from backend.utils.email_utils import send_email
from backend.utils.password_utils import get_password_hash
from backend.core.base_service import TraceableService
class AccountService(TraceableService):
    def __init__(self, db: AsyncSession , user_repo : UserRepository):
        self.db = db
        self.user_repo = user_repo

    async def signup(self, request):
        if request.password != request.confirm_password:
            return error_response(code=400, error_message="Passwords do not match")

        if await self.user_repo.get_user_by_username(request.username):
            return error_response(code=400, error_message="Username already exists")

        await self.user_repo.create_user(request.username, request.password, request.email)
        code = str(random.randint(100000, 999999))
        await self.user_repo.save_reset_code(request.email, code)
        send_email(request.email, "Verify Your Account", f"Your verification code is: {code}")
        return success_response(code=201, data={"message": "Account created. Please verify."})

    async def verify_account(self, request):
        email = await self.user_repo.get_email_by_code(request.code)
        if not email or not await self.user_repo.verify_reset_code(email, request.code):
            return error_response(code=400, error_message="Invalid or expired code")

        user = await self.user_repo.get_user_by_email(email)
        if not user:
            return error_response(code=404, error_message="User not found")

        if request.new_password:
            user.hashed_password = get_password_hash(request.new_password)
            await self.db.commit()
            await self.db.refresh(user)
            return success_response(code=200, data={"message": "Password reset successful"})

        await self.user_repo.update_verification_status(email)
        return success_response(code=200, data={"message": "Verification successful"})

    async def resend_verification_code(self, request):
        user = await self.user_repo.get_user_by_email(request.email)
        if not user:
            return error_response(code=404, error_message="User not found")
        if user.is_verified:
            return error_response(code=400, error_message="Account already verified")

        code = str(random.randint(100000, 999999))
        await self.user_repo.save_reset_code(request.email, code)
        send_email(user.email, "Resend Code", f"Code: {code}")
        return success_response(code=200, data={"message": "Verification code resent"})
