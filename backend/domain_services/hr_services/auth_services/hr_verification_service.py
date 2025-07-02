import random, asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.response_schemas import success_response, error_response
from backend.utils.email_utils import send_email
from backend.data_access.postgres.hr.hr_auth_repository import HRRepository

class HRVerificationService:
    def __init__(self, db: AsyncSession , hr_repo : HRRepository):
        self.db = db
        self.hr_repo = hr_repo
    async def verify_code(self, code: str):
        email = await self.hr_repo.get_email_by_code(code)
        if not email:
            return error_response(code=400, error_message="Invalid or expired verification code")

        is_valid = await self.hr_repo.verify_reset_code(email, code)
        if not is_valid:
            return error_response(code=400, error_message="Invalid or expired verification code")

        await self.hr_repo.update_verification_status(email)
        return success_response(code=200, data={"message": "HR account verified successfully."})

    async def resend_code(self, email: str):
        hr = await self.hr_repo.get_by_email(email)
        if not hr:
            return error_response(code=404, error_message="HR user not found")

        if hr.is_verified:
            return error_response(code=400, error_message="Account already verified")

        new_code = str(random.randint(100000, 999999))
        await self.hr_repo.save_reset_code(email, new_code)

        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                send_email,
                hr.business_email,
                "Resend Verification Code",
                f"Your new verification code is: {new_code}"
            )
        except Exception as e:
            return error_response(code=500, error_message=f"Failed to send email: {str(e)}")

        return success_response(code=200, data={"message": "Verification code resent successfully"})
