from backend.utils.response_schemas import success_response, error_response
from backend.data_access.mongo.home.home_stats_repository import HomeStatsRepository

class HomeStatsService:
    def __init__(self, repository: HomeStatsRepository):
        self.repository = repository

    async def get_summary(self, user_id: int):
        try:
            user_id = int(user_id)
            summary = await self.repository.fetch_user_summary(user_id)

            result = {
                "total_interviews": summary.get("total_interviews", 0),
                "total_answers": summary.get("total_answers", 0),
                "avg_score": summary.get("avg_score", 0.0),
                "accuracy": summary.get("accuracy", 0.0),
            }

            return success_response(code=200, data=result)

        except Exception as e:
            return error_response(code=500, error_message=f"Summary error: {str(e)}")
