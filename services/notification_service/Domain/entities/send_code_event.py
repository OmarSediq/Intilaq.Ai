
from dataclasses import dataclass
@dataclass(frozen=True)
class SendCodeEvent:
    email:str
    verification_code:str
    idempotency_key: str



    