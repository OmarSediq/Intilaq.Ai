from datetime import datetime
import secrets
from backend.core.contracts.events.event_envelope import EventEnvelope
from backend.data_access.postgres.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.generate_ulid_utils import generate_ulid
from backend.utils.response_schemas import success_response, error_response
from backend.core.base_service import TraceableService
from backend.core.contracts.publishers.email_event_publisher import EmailEventPublisher
class PasswordRecoveryService(TraceableService):
    def __init__(self, db: AsyncSession , user_repo : UserRepository , email_event_publisher: EmailEventPublisher ):
        self.db = db
        self.user_repo =user_repo
        self.email_event_publisher = email_event_publisher

    async def forgot_password(self, request):
        user = await self.user_repo.get_user_by_email(request.email)
        if not user:
            return error_response(code=404, error_message="Email not found")

        code = str(secrets.randbelow(900000)+100000)
        await self.user_repo.save_reset_code(request.email, code)
        await self.db.commit()

        event= EventEnvelope(
          event_name="notification.email.password_reset",
            version=1,
            occurred_at=datetime.utcnow(),
            idempotency_key=generate_ulid(),
            payload={
                "email": request.email,
                "verification_code": code,
            }
        )
        try:
         await self.email_event_publisher.publish(event)
        except Exception:
        # intentionally ignored (best-effort)
         pass

        return success_response(code=200, data={"message": "Reset code sent"})
