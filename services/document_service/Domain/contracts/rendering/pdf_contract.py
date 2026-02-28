from abc import ABC, abstractmethod


class PdfContract(ABC):
    @abstractmethod
    async def render(self, html: str) -> bytes:
  
        pass 

    