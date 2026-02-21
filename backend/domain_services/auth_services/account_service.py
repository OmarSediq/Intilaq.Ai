from datetime import datetime
from backend.data_access.postgres.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.generate_ulid_utils import generate_ulid
from backend.utils.response_schemas import success_response, error_response
from backend.utils.password_utils import get_password_hash
from backend.core.contracts.publishers.email_event_publisher import EmailEventPublisher
from backend.core.contracts.events.event_envelope import EventEnvelope
from backend.core.base_service import TraceableService
import secrets
class AccountService(TraceableService):
    def __init__(self, db: AsyncSession , user_repo : UserRepository  ,email_event_publisher: EmailEventPublisher
):
        self.db = db
        self.user_repo = user_repo
        self.email_event_publisher = email_event_publisher


    async def signup(self, request):
        if request.password != request.confirm_password:
            return error_response(code=400, error_message="Passwords do not match")

        if await self.user_repo.get_user_by_username(request.username):
            return error_response(code=400, error_message="Invalid email or password")

        await self.user_repo.create_user(request.username, request.password, request.email)
        code = str(secrets.randbelow(900000)+100000)
        await self.user_repo.save_reset_code(request.email, code)
        await self.db.commit()

        event = EventEnvelope(
            event_name="notification.email.verification_code",
            version=1,
            occurred_at=datetime.utcnow(),
            idempotency_key=generate_ulid(),
            payload={
                "email":request.email,
                "verification_code":code,
                
            },
        )

        try:
            await self.email_event_publisher.publish(event)
        except Exception:
            # intentionally ignored (best-effort)
            pass
    
        return success_response(code=201, data={"message": "Account created. Please verify."})



        
        # send_email(request.email, "Verify Your Account", f"Your verification code is: {code}")

    async def verify_account(self, request):
        email = await self.user_repo.get_email_by_code(request.code)
        if not email or not await self.user_repo.verify_reset_code(email, request.code):
            return error_response(code=400, error_message="If this email is eligible, you will receive a verification message.")

        user = await self.user_repo.get_user_by_email(email)
        if not user:
            return error_response(code=404, error_message="If this email is eligible, you will receive a verification message.")

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
            return error_response(code=404, error_message="Invalid email or password")
        if user.is_verified:
            return error_response(code=400, error_message="Invalid email or password")

        code = str(secrets.randbelow(900000)+100000)
        await self.user_repo.save_reset_code(request.email, code)

        await self.db.commit()
        event = EventEnvelope(
            event_name="notification.email.verification_code",
            version=1,
            occurred_at=datetime.utcnow(),
            idempotency_key=f"verify:{request.email}:{code}",
            payload={
                "email":request.email,
                "verification_code":code,
                
            },
        )
        try:
            await self.email_event_publisher.publish(event)
        except Exception:
            # intentionally ignored (best-effort)
            pass

        # send_email(user.email, "Resend Code", f"Code: {code}")
        return success_response(code=200, data={"message": "Verification code resent"})
