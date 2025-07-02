from backend.core.base_service import TraceableService
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from typing import Dict, List
from datetime import datetime, timezone
from backend.data_access.mongo.hr.hr_summary_repository import HRSummaryRepository
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from backend.utils.status_utils import compute_evaluation_status
from backend.utils.date_utils import parse_date_range

class HRUserSummaryService(TraceableService):
    def __init__(self,answer_repo: HRAnswerRepository , interview_repo: HRInterviewRepository,  summary_repo: HRSummaryRepository,) :
        self.answer_repo = answer_repo
        self.interview_repo = interview_repo
        self.summary_repo = summary_repo


    async def get_overall_score(self, interview_token: str, user_email: str) -> float:
        session = await self.answer_repo.get_session_by_token_and_email(interview_token, user_email)
        if not session:
            raise ValueError("Session not found")

        overall = session.get("overall_score")
        if overall is None:
            raise ValueError("Overall score not calculated yet")

        return overall

    async def update_review_status(self, interview_token: str, user_email: str, status: str) -> Dict:
        await self.answer_repo.set_review_status(interview_token, user_email, status)

        await self.list_participants(interview_token)
        return {"review_status": status}

    async def list_participants(self, interview_token: str) -> List[Dict]:
        interview_doc = await self.interview_repo.get_by_token(interview_token)
        if not interview_doc:
            raise ValueError(f"Interview token '{interview_token}' not found")

        role = interview_doc.get("job_title") or interview_doc.get("role")
        date_range = interview_doc.get("date_range")
        start_end = parse_date_range(date_range)
        hr_id = interview_doc.get("hr_id")

        sessions = await self.answer_repo.collection.find(
            {"interview_token": interview_token},
            {"user_name": 1, "user_email": 1, "review_status": 1, "login_time": 1, "_id": 0}
        ).to_list(None)

        sessions_by_email = {s["user_email"]: s for s in sessions}
        candidate_emails = interview_doc.get("candidate_emails", [])

        summaries: List[Dict] = []
        now = datetime.now(timezone.utc)

        for email in candidate_emails:
            sess = sessions_by_email.get(email)
            summaries.append(
                {
                    "user_name": sess.get("user_name") if sess else None,
                    "user_email": email,
                    "role": role,
                    "date": date_range,
                    "review_status": sess.get("review_status") if sess else "pending",
                    "evaluation_status": compute_evaluation_status(sess, start_end, now),
                }
            )

        summary_doc = {
            "interview_token": interview_token,
            "hr_id": hr_id,
            "role": role,
            "date_range": date_range,
            "participants": summaries,
        }

        await self.summary_repo.upsert(interview_token, summary_doc)

        return summaries


    async def get_dashboard(self, hr_id: int) -> Dict:
        interviews = await self.summary_repo.get_interview_stats_for_hr(hr_id)

        total_candidates = sum(i["num_candidates"] for i in interviews)

        return {
            "total_candidates": total_candidates,
            "interviews": interviews
        }

    async def get_interview_participants(
            self, interview_token: str, hr_id: int
    ) -> Dict:
        participants = await self.summary_repo.get_participants_for_interview(
            interview_token, hr_id
        )
        if participants is None:
            raise ValueError("Interview not found or access denied")

        return {
            "interview_token": interview_token,
            "hr_id": hr_id,
            "participants": participants
        }
