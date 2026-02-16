from datetime import datetime, time, timezone
from typing import Tuple

def parse_date_range(date_range: str) -> Tuple[datetime, datetime]:
    from datetime import datetime, timezone
    start_str, end_str = date_range.split(" to ")
    start = datetime.strptime(start_str.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = datetime.strptime(end_str.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return start, end

def parse_iso(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except Exception:
        raise ValueError(f"Invalid ISO datetime: {value}")
