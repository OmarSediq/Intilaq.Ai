from abc import ABC , abstractmethod
from typing import Dict , Any


class CvSnapshotRepository(ABC):
    @abstractmethod
    async def get_by_id (self , snapshot_id :str )-> Dict[str , Any]:
        pass 