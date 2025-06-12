from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from backend.core.base_service import TraceableService
from backend.utils.response_schemas import success_response, error_response
from backend.data_access.mongo.hr.hr_invitation_repository import HRInvitationRepository
from backend.data_access.postgres.hr.hr_user_repository import HRUserRepository
from backend.core.job_triggers.email_job_trigger_service import EmailJobTriggerService

class HRInvitationService(TraceableService):
    def __init__(self, repo: HRInvitationRepository, db: AsyncSession, email_trigger: EmailJobTriggerService):
        self.repo = repo
        self.db = db
        self.email_trigger = email_trigger

    async def send_invitations(self, interview_token: str, emails: list, email_description: str, interview_link: str):
        doc = await self.repo.get_interview_by_token(interview_token)
        if not doc:
            return error_response(code=404, error_message="Interview not found.")

        job_title = doc.get("job_title", "Unknown")
        raw_date = doc.get("specific_date", doc.get("date_range", "Not Set"))

        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
        except Exception:
            parsed_date = raw_date

        hr_id = doc.get("hr_id")

        hr_repo = HRUserRepository(self.db)
        company_field = await hr_repo.get_company_field_by_hr_id(hr_id)

        await self.repo.update_interview_metadata(interview_token, {
            "candidate_emails": emails,
            "email_description": email_description,
            "interview_link": interview_link,
            "company_field": company_field
        })

        self.email_trigger.trigger_send_invitation_job(
            emails=emails,
            job_title=job_title,
            raw_date=raw_date,
            interview_link=interview_link,
            hr_id=hr_id
        )

        return success_response(code=200, data={"message": "Emails queued and metadata updated."})
