import random, asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.db_services import get_email_by_code_hr, verify_hr_reset_code, update_hr_verification_status, get_hr_by_email, save_hr_reset_code
from app.utils.response_schemas import success_response, error_response
from app.utils.email_utils import send_email

class HRVerificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def verify_code(self, code: str):
        email = await get_email_by_code_hr(code, self.db)
        if not email:
            return error_response(code=400, error_message="Invalid or expired verification code")

        is_valid = await verify_hr_reset_code(email, code, self.db)
        if not is_valid:
            return error_response(code=400, error_message="Invalid or expired verification code")

        await update_hr_verification_status(email, self.db)
        return success_response(code=200, data={"message": "HR account verified successfully."})

    async def resend_code(self, email: str):
        hr = await get_hr_by_email(email, self.db)
        if not hr:
            return error_response(code=404, error_message="HR user not found")

        if hr.is_verified:
            return error_response(code=400, error_message="Account already verified")

        new_code = str(random.randint(100000, 999999))
        await save_hr_reset_code(email, new_code, self.db)

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
