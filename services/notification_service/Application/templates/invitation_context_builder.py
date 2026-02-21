from datetime import datetime
from typing import Optional, Dict


def build_invitation_context(
    *,
    candidate_name: str,
    job_title: str,
    interview_date: datetime,
    interview_link: str,
    company_field: Optional[str],
) -> Dict[str, str]:

    return {
        "candidate_name": candidate_name,
        "job_title": job_title,
        "interview_date": interview_date,
        "interview_link": interview_link,
        "company_field": company_field or "",
    }
