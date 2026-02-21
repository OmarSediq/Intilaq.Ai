from Domain.entities.send_code_event import SendCodeEvent
from Domain.contracts.event_envelope import EventEnvelope


def map_envelope_to_send_code_event(
    envelope: EventEnvelope,
) -> SendCodeEvent:

    payload = envelope.payload

    return SendCodeEvent(
        email=payload["email"],
        verification_code=payload["verification_code"],
        idempotency_key=envelope.idempotency_key,
    )
