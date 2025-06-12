import asyncio
from datetime import datetime
from backend.core.email.email_sender_service import EmailSenderService
from backend.core.email.email_template_service import EmailTemplateService
from backend.data_access.postgres.hr.hr_user_repository import HRUserRepository
from backend.core.providers.infra_providers import get_postgres_session
from backend.utils.string_utils import extract_name_from_email

def send_invitation_job(emails: list, job_title: str, raw_date: str, interview_link: str, hr_id: int):
    async def _internal():
        try:
            try:
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
            except Exception:
                parsed_date = raw_date

            async for session in get_postgres_session():
                hr_repo = HRUserRepository(session)
                company_field = await hr_repo.get_company_field_by_hr_id(hr_id)

                template_service = EmailTemplateService()
                sender_service = EmailSenderService()

                for email in emails:
                    candidate_name = extract_name_from_email(email)

                    html_body = template_service.render_invitation(
                        candidate_name=candidate_name,
                        job_title=job_title,
                        interview_date=parsed_date,
                        interview_link=interview_link,
                        company_field=company_field
                    )

                    subject = f"Interview Invitation - {job_title}"
                    sender_service.send_email(to_email=email, subject=subject, html_body=html_body)

                print(f"[SUCCESS] Emails sent to {len(emails)} candidates.")

        except Exception as e:
            print(f"[ERROR] Failed to send invitations: {str(e)}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_internal())
    finally:
        loop.close()
