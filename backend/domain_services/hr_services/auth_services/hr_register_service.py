from datetime import datetime
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.generate_ulid_utils import generate_ulid
from backend.utils.response_schemas import success_response, error_response
from backend.data_access.postgres.hr.hr_auth_repository import HRRepository
from backend.core.contracts.publishers.email_event_publisher import EmailEventPublisher
from backend.core.contracts.events.event_envelope import EventEnvelope

class HRRegisterService:
    def __init__(self, db: AsyncSession , hr_repo: HRRepository , email_event_publisher : EmailEventPublisher):
        self.db = db
        self.hr_repo = hr_repo
        self.email_event_publisher = email_event_publisher

    async def register(self, request):
        if request.password != request.confirm_password:
            return error_response(code=400, error_message="If this email is eligible, you will receive a verification message.")

        existing_hr = await self.hr_repo.get_by_email(request.business_email)
        if existing_hr:
            return error_response(code=400, error_message="If this email is eligible, you will receive a verification message.")

        await self.hr_repo.create(request)
        code = str(secrets.randbelow(900000)+100000)
        await self.hr_repo.save_reset_code(request.business_email, code)
        await self.db.commit()
        event = EventEnvelope(
            event_name="notification.email.hr_verification_code",
            version=1,
            occurred_at=datetime.utcnow(),
            idempotency_key=generate_ulid(),
            payload={
                "email": request.business_email,
                "verification_code": code,
            },
        )
        try:
             await self.email_event_publisher.publish(event)
        except Exception:
            pass
        
        # send_email(request.business_email, "Verify your HR account", f"Your code is: {code}")
        return success_response(code=201, data={"message": "If this email is eligible, you will receive a verification message."})
