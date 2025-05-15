from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.response_schemas import success_response, error_response

class HomeStatsService:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.collection = mongo_client["interview_db"]["user_home_summary"]
    async def get_summary(self, user_id: int):
        try:
            print("USER ID:", user_id, type(user_id))
            user_id = int(user_id)

         
            summary = await self.collection.find_one(
                {"user_id": user_id},
                {"_id": 0, "total_interviews": 1, "total_answers": 1, "avg_score": 1, "accuracy": 1}
            ) or {}

            
            summary = {
                "total_interviews": summary.get("total_interviews", 0),
                "total_answers": summary.get("total_answers", 0),
                "avg_score": summary.get("avg_score", 0.0),
                "accuracy": summary.get("accuracy", 0.0),
            }

            return success_response(code=200, data=summary)

        except Exception as e:
            return error_response(code=500, error_message=f"Summary error: {str(e)}")
