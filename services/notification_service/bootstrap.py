
from Application.use_cases.process_invitation import ProcessInvitationUseCase
from Application.Handlers.notification_handler import NotificationHandler

from infra.Email.smtp_sender import EmailSenderService
from infra.stream_client import RedisStreamClient
from infra.redis_client import get_redis
from Domain.policies.retry_policy import RetryPolicy
from Core.logging_config import configure_logging
from Application.use_cases.send_auth_code import SendAuthCodeEmailUseCase
from Application.Mappers.send_code_event_mapper import map_envelope_to_send_code_event
from Application.Mappers.invitation_event_mapper import map_envelope_to_invitation_event


async def bootstrap():
    # 1️⃣ logging
    configure_logging("notification_service")

    # 2️⃣ infra init
    redis = await get_redis()
    stream = RedisStreamClient(redis)

    # ✅ create consumer group هنا
    await stream.ensure_group()

    # 3️⃣ business wiring
    email_sender = EmailSenderService()

    retry_policy = RetryPolicy(
        max_attempts=1,
        dlq=None,
    )

    process_invitation_use_case = ProcessInvitationUseCase(
        email_sender=email_sender,
        retry_policy=retry_policy,
    )

    send_auth_code_use_case = SendAuthCodeEmailUseCase (
        email_sender=email_sender,
        retry_policy=retry_policy,

    )

    notification_handler = NotificationHandler(
        
    routes={
        "notification.email.verification_code": (
            map_envelope_to_send_code_event,
            send_auth_code_use_case,
        ),
        "notification.email.password_reset": (
            map_envelope_to_send_code_event,
            send_auth_code_use_case,
        ),
        "notification.email.hr_verification_code": (
            map_envelope_to_send_code_event,
            send_auth_code_use_case,
        ),
        "notification.email.hr_verification_code.resend": (
            map_envelope_to_send_code_event,
            send_auth_code_use_case,
        ),

        "notification.email.interview_invitation": (
            map_envelope_to_invitation_event,
            process_invitation_use_case,
        ),
    }
)


    return {
        "notification_handler": notification_handler,
        "stream": stream,
    }
