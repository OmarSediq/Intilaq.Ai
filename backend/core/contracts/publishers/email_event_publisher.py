from abc import ABC, abstractmethod
from backend.core.contracts.events.event_envelope import EventEnvelope
## event publisher interface
class EmailEventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: EventEnvelope) -> None:
        """
        Publish an email-related domain event.
        The event must be self-contained and ready for execution.
        """
        raise NotImplementedError
