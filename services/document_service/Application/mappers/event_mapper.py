from datetime import datetime
from Domain.contracts.events.event_envelope import EventEnvelope
from Domain.contracts.events.document_events import DocumentGenerationRequested

class EventMapper: 
    @staticmethod
    def to_envelope(raw_event: dict)-> EventEnvelope:
        return EventEnvelope(
            event_name=raw_event["event_name"],
            version=raw_event["version"],
            occurred_at=datetime.fromisoformat(raw_event["occurred_at"]),
            idempotency_key=raw_event["idempotency_key"],
            payload=raw_event["payload"],
        )
    

    @staticmethod
    def to_document_request (envelope: EventEnvelope) -> DocumentGenerationRequested:
        payload = envelope.payload
        return DocumentGenerationRequested(
            snapshot_id=payload["snapshot_id"],
            document_type=payload["document_type"],
            formats=payload["formats"],
            idempotency_key = envelope.idempotency_key
        )
    