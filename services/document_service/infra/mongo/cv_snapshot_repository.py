from Domain.contracts.mongo.snapshot_contract import CvSnapshotRepository


class MongoCvSnapshotRepository(CvSnapshotRepository):
    def __init__ (self , db):
        self.collection = db["cv_snapshots"]

    async def get_by_id (self , snapshot_id : str )-> dict:
        snapshot = await self.collection.find_one(
        
            {"_id": snapshot_id} 
        )

        if not snapshot:
            raise ValueError("Snapshot not found")
        return snapshot