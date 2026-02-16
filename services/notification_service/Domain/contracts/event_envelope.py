from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class EventEnvelope:
    event_name: str
    version: int
    occurred_at: datetime
    idempotency_key: str
    payload: Dict[str, Any]
    _message_id: Optional[str] = None


