from datetime import datetime, timezone, date
from typing import Dict, Optional, Tuple

def compute_evaluation_status(
    session: Optional[Dict],
    start_end: Tuple[datetime, datetime],
    now: datetime | None = None
) -> str:
    now = now or datetime.now(timezone.utc)
    start_dt, end_dt = start_end

    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)

    if not session:
        return "Missed" if now > end_dt else "Pending"

    review_status = session.get("review_status", "pending")
    if review_status in ("accepted", "rejected"):
        return "Reviewed"

    login_time: datetime | None = session.get("login_time")
    if not login_time:
        return "Missed" if now > end_dt else "Pending"

    if login_time.tzinfo is None:
        login_time = login_time.replace(tzinfo=timezone.utc)

    if start_dt <= login_time <= end_dt:
        return "Pending"

    return "Missed"
