from abc import ABC 
from typing import Dict , Any


class CvSnapshotRepository(ABC):
    async def get_by_id (self , snapshot_id :str )-> Dict[str , Any]:
        pass 