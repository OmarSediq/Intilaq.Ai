from dataclasses import dataclass 
from typing import List


@dataclass(frozen=True)
class DocumentGenerationRequested:
        snapshot_id: str
        document_type: str
        formats: List[str]
        idempotency_key:str