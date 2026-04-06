from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection

class CVSnapshotRepository :
    def __init__(self , db:AsyncIOMotorCollection):
        self.collection = db["cv_snapshots"] 

    async def create_snapshot (
            self,
            snapshot_id:str,
            user_id: int,
            data:Dict[str , Any],
            version: int=1,
        
    )-> str:
        doc={
            "_id":snapshot_id,
            "type":"cv",
            "user_id": user_id,
            "version":version,
            "data":data,
            "created_at":datetime.utcnow()
        }
        await self.collection.insert_one(doc)
        return snapshot_id
    

    async def get_snapshot( self , snapshot_id: str)-> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"_id" :snapshot_id})


   
    


    #   async def get_latest_by_user(self, user_id: int):
    #     return await self.collection.find_one(
    #         {"user_id": user_id},
    #         sort=[("created_at", -1)]
    #     )
    