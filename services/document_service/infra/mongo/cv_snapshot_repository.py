from Domain.contracts.mongo.snapshot_contract import CvSnapshotRepository


class MongoCvSnapshotRepository(CvSnapshotRepository):
    def __init__ (self , db):
        self.collection = db["cv_snapshots"]

    async def get_by_id(self, snapshot_id: str) -> dict:
        print("---- DEBUG SNAPSHOT LOOKUP ----")
        print("DB:", self.collection.database.name)
        print("Collection:", self.collection.name)
        print("Snapshot ID VALUE:", repr(snapshot_id))
        print("Snapshot ID TYPE:", type(snapshot_id))

        count = await self.collection.count_documents({})
        print("Total documents in collection:", count)

        first_doc = await self.collection.find_one({})
        print("First document sample:", first_doc)

        snapshot = await self.collection.find_one({"_id": snapshot_id})

        if not snapshot:
            raise ValueError(
                f"Snapshot not found | queried_id={repr(snapshot_id)} | total_docs={count}"
            )

        return snapshot


    