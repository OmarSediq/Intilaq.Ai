from abc import ABC, abstractmethod

from typing import Dict


class EmailSender(ABC):
    @abstractmethod
    async def send_email(
        self,
        *,
        to_email: str,
        template: str,
        context: Dict,
    ) -> None:
        raise NotImplementedError
