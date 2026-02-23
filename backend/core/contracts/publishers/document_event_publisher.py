from abc import ABC , abstractmethod
from backend.core.contracts.events.event_envelope import EventEnvelope

class DocumentEventPublisher(ABC):
    @abstractmethod
    async def publish (self , event : EventEnvelope) -> None:

        raise NotImplementedError
