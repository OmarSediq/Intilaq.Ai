from abc import ABC, abstractmethod
from typing import Dict, Any


class DocxContract(ABC):
    @abstractmethod
    async def render(self, snapshot: Dict[str, Any]) -> bytes:

         pass
