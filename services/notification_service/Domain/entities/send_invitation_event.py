from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass(frozen=True)
class SendInvitationEvent:
    emails: Dict[str, dict] | List[str]
    job_title: str
    interview_date: datetime
    interview_link: str
    company_field: Optional[str]
    idempotency_key: str
