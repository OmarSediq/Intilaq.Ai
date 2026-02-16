
from Domain.entities.send_invitation_event import SendInvitationEvent
from Domain.contracts.event_envelope import EventEnvelope
from utils.date_utils import parse_iso

def map_envelope_to_invitation_event(envelope: EventEnvelope) -> SendInvitationEvent:
    payload = envelope.payload
    return SendInvitationEvent(
        
        emails=payload["emails"],
        job_title=payload["job_title"],
        interview_date=parse_iso(payload["interview_date"]),
        interview_link=payload["interview_link"],
        company_field=payload.get("company_field"),
        idempotency_key=envelope.idempotency_key,
    )
