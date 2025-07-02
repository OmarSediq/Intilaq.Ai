from typing import List, Dict, Optional
from pymongo import ASCENDING

class HRSummaryRepository:
    def __init__(self, db):
        self.collection = db["hr_summary"]

    async def upsert(self, interview_token: str, doc: Dict):
        await self.collection.update_one(
            {"interview_token": interview_token},
            {
                "$set": {
                    "participants": doc["participants"],
                    "role": doc["role"],
                    "date_range": doc["date_range"],
                    "hr_id": doc["hr_id"],
                },
                "$setOnInsert": {"interview_token": interview_token},
            },
            upsert=True
        )

    async def get_interview_stats_for_hr(self, hr_id: int) -> List[Dict]:

        pipeline = [
            {"$match": {"hr_id": hr_id}},
            {"$project": {
                "_id": 0,
                "interview_token": 1,
                "role": 1,
                "num_candidates": {"$size": "$participants"},
                "pending_candidates": {
                    "$size": {
                        "$filter": {
                            "input": "$participants",
                            "as": "p",
                            "cond": {"$eq": ["$$p.review_status", "pending"]}
                        }
                    }
                }
            }},
            {"$sort": {"interview_token": ASCENDING}}
        ]
        return await self.collection.aggregate(pipeline).to_list(None)

    async def get_participants_for_interview(
            self, interview_token: str, hr_id: int
    ) -> Optional[List[Dict]]:

        doc = await self.collection.find_one(
            {"interview_token": interview_token, "hr_id": hr_id},
            {"_id": 0, "participants": 1}
        )
        if not doc:
            return None
        return doc.get("participants", [])
