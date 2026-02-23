
from Domain.entities.send_code_event import SendCodeEvent
from Domain.contracts.email_sender import EmailSender
from infra.Email.template_renderer import render_email_template
from Application.templates.verification_context_builder import build_verification_context
from Domain.policies.retry_policy import RetryPolicy


class SendAuthCodeEmailUseCase:

    def __init__(
            self,
            email_sender: EmailSender,
            retry_policy: RetryPolicy
            ):
            self.email_sender = email_sender 
            self.retry_policy = retry_policy

    async def execute(self, event: SendCodeEvent) -> None:

        context = build_verification_context(
            verification_code=event.verification_code
        )

        html_body = render_email_template(
            template_name="email_template",
            context=context
        )
        subject = "Verify Your Account"

        await self.retry_policy.run(
            key=event.idempotency_key,
            action=lambda: self.email_sender.send_email(
                to_email=event.email,
                subject=subject,
                html_body=html_body,
            ),
        )

    


    



        
        
        
