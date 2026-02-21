from datetime import datetime
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.response_schemas import success_response, error_response
from backend.data_access.postgres.hr.hr_auth_repository import HRRepository
from backend.core.contracts.events.event_envelope import EventEnvelope
from backend.core.contracts.publishers.email_event_publisher import EmailEventPublisher
from backend.utils.generate_ulid_utils import generate_ulid
class HRVerificationService:
    def __init__(self, db: AsyncSession , hr_repo : HRRepository , email_event_publisher : EmailEventPublisher):
        self.db = db
        self.hr_repo = hr_repo
        self.email_event_publisher = email_event_publisher

    async def verify_code(self, code: str):
        email = await self.hr_repo.get_email_by_code(code)
        if not email:
            return error_response(code=400, error_message="Invalid or expired verification code")

        is_valid = await self.hr_repo.verify_reset_code(email, code)
        if not is_valid:
            return error_response(code=400, error_message="Invalid or expired verification code")

        await self.hr_repo.update_verification_status(email)
        await self.db.commit()
        return success_response(code=200, data={"message": "HR account verified successfully."})

    async def resend_code(self, email: str):
        hr = await self.hr_repo.get_by_email(email)
        if not hr:
            return error_response(code=404, error_message="HR user not found")

        if hr.is_verified:
            return error_response(code=400, error_message="Account already verified")

        new_code =str(secrets.randbelow(900000)+100000)

        await self.hr_repo.save_reset_code(email, new_code)
        await self.db.commit()

        event = EventEnvelope(
            event_name="notification.email.hr_verification_code.resend",
            version=1,
            occurred_at=datetime.utcnow(),
            idempotency_key=generate_ulid(),
            payload={
                "email": email,
                "verification_code": new_code,
            },
        )
        try:
            await self.email_event_publisher.publish(event)
        except Exception:
            pass
        # try:
        #     await asyncio.get_event_loop().run_in_executor(
        #         None,
        #         send_email,
        #         hr.business_email,
        #         "Resend Verification Code",
        #         f"Your new verification code is: {new_code}"
        #     )
        # except Exception as e:
        #     return error_response(code=500, error_message=f"Failed to send email: {str(e)}")

        return success_response(code=200, data={"message": "Verification code resent successfully"})
