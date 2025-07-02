from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository

class HRAnswerScoringService:
    def __init__(self, repo: HRAnswerRepository):
        self.repo = repo

    async def set_score_for_answer(
        self,
        interview_token: str,
        user_email: str,
        index: int,
        score: float | None = None,
        extra_fields: dict | None = None,
    ):
        update = (extra_fields or {}) | ({"score": score} if score is not None else {})
        await self.repo.update_answer_by_index(
            interview_token, user_email, index, update
        )
        await self._maybe_set_overall(interview_token, user_email)

    async def _maybe_set_overall(self, interview_token: str, user_email: str):
        doc = await self.repo.get_session_by_token_and_email(
            interview_token, user_email
        )
        questions = await self._get_total_questions(interview_token)
        scored = [a.get("score") for a in doc["answers"] if a.get("score") is not None]
        if len(scored) == questions:
            overall = round(sum(scored) / (questions * 10) * 100, 2)
            await self.repo.set_overall_score(interview_token, user_email, overall)

    async def _get_total_questions(self, interview_token: str) -> int:
        coll = self.repo.collection.database["hr_interview_questions"]
        qdoc = await coll.find_one({"interview_token": interview_token}, {"questions": 1})
        return len(qdoc.get("questions", [])) if qdoc else 0
