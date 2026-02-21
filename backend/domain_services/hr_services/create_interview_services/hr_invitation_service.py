from datetime import datetime
from backend.core.base_service import TraceableService
from backend.utils.response_schemas import success_response, error_response
from backend.data_access.mongo.hr.hr_invitation_repository import HRInvitationRepository
from backend.data_access.postgres.hr.hr_user_repository import HRUserRepository
from backend.core.contracts.publishers.email_event_publisher import EmailEventPublisher
from backend.core.contracts.events.event_envelope import EventEnvelope
from backend.utils.generate_ulid_utils import generate_ulid
class HRInvitationService(TraceableService):

    def __init__(
        self,
        repo: HRInvitationRepository,
        hr_repo :HRUserRepository,
        email_event_publisher: EmailEventPublisher
    ):
        self.repo = repo
        self.hr_repo = hr_repo
        self.email_event_publisher = email_event_publisher

    async def send_invitations(
        self,
        interview_token: str,
        emails: list,
        email_description: str,
        interview_link: str
    ):
        doc = await self.repo.get_interview_by_token(interview_token)
        if not doc:
            return error_response(code=404, error_message="Interview not found.")

        job_title = doc.get("job_title", "Unknown")
        raw_date = doc.get("specific_date", doc.get("date_range"))

        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
        except Exception:
            parsed_date = datetime.utcnow()

        hr_id = doc.get("hr_id")

        
        company_field = await self.hr_repo.get_company_field_by_hr_id(hr_id)


        await self.repo.update_interview_metadata(interview_token, {
            "candidate_emails": emails,
            "email_description": email_description,
            "interview_link": interview_link,
            "company_field": company_field
        })

        event = EventEnvelope(
                event_name="notification.email.interview_invitation",
                version=1,
                occurred_at=datetime.utcnow(),
                idempotency_key=generate_ulid(),
                payload={
                    "emails": emails,
                    "job_title": job_title,
                    "interview_date": parsed_date.isoformat(),
                    "interview_link": interview_link,
                    "company_field": company_field,
                    "email_description": email_description,
                    "created_at": datetime.utcnow().isoformat(),
                },
            )

        await self.email_event_publisher.publish(event)

        return success_response(
                code=200,
                data={"message": "Invitation emails scheduled."},
            )