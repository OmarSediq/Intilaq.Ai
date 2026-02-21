from Domain.entities.send_invitation_event import SendInvitationEvent
from Domain.contracts.email_sender import EmailSender
from Domain.policies.retry_policy import RetryPolicy
from infra.Email.template_renderer import render_email_template
from utils.string_utils import extract_name_from_email
from Application.templates.invitation_context_builder import build_invitation_context


class ProcessInvitationUseCase:

    def __init__(
        self,
        email_sender: EmailSender,
        retry_policy: RetryPolicy,
    ):
        self.email_sender = email_sender
        self.retry_policy = retry_policy

    async def execute(self, event: SendInvitationEvent) -> None:

        for email in event.emails:

            candidate_name = extract_name_from_email(email)

            context = build_invitation_context(
                candidate_name=candidate_name,
                job_title=event.job_title,
                interview_date=event.interview_date,
                interview_link=event.interview_link,
                company_field=event.company_field,
            )

            html_body = render_email_template(
                template_name="interview_invitation",
                context=context,
            )

            subject = f"Interview Invitation - {event.job_title}"

            await self.retry_policy.run(
                key=f"{event.idempotency_key}",
                action=lambda: self.email_sender.send_email(
                    to_email=email,
                    subject=subject,
                    html_body=html_body,
                ),
            )

