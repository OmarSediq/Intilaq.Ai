

from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase


class  UserCVStateRepository:

    def __init__ (self , db :AsyncIOMotorDatabase):
         self.collection = db["user_cv_state"]

    ## Create Index 
    async def ensure_indexes(self):
            await self.collection.create_index("user_id" , unique=True)

     ## 
    async def ensure_user_state (self, user_id : int)-> None : 
         await self.collection.update_one(
              {"user_id": user_id},
              {
                   "$setOnInsert":{
                        "user_id": user_id,
                        "Created_at":datetime.utcnow()
                   }
              },
              upsert=True
         )


    ## Set Current Snapshot
    async def set_current_snapshot(self , user_id , snapshot_id)->None:
        await  self.collection.update_one(
             {"user_id" : user_id},
             {
                  "$set":{
                       "current_snapshot_id": snapshot_id,
                       "updated_at":datetime.utcnow()
                  
                  },
                    "$setOnInsert": {
                         "created_at": datetime.utcnow()
                    }
                },
          
            upsert =True
        )

    ## Get Current Snapshot ID 
    async def get_current_snapshot_id(self , user_id)-> Optional[str]:
        doc = await self.collection.find_one(
             {"user_id" : user_id},
             {"current_snapshot_id": 1}
        )
        if  not doc: 
             return None 
        return doc.get("current_snapshot_id")
    
         


         


        
        
