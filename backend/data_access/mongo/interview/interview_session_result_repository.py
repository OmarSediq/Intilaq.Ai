from backend.core.base_service import TraceableService

from motor.motor_asyncio import AsyncIOMotorDatabase

class InterviewSessionResultRepository(TraceableService):
    def __init__(self , db : AsyncIOMotorDatabase): 
        self.collection = db["session_results"]

         
    async def save_session_result(self, data: dict):
        return await self.db["session_results"].insert_one(data)

   