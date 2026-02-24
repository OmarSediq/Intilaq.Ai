class CVSnapshotRepository:
    def __init__(self, db):
        self._collection = db["cv_snapshots"]

    async def get_snapshot(self, snapshot_id: str) -> dict | None:
        return await self._collection.find_one(
            {"snapshot_id": snapshot_id},
            {"_id": 0},
        )
