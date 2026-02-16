# backend/core/job_processors/process_send_invitation_job.py
import os
import traceback
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from backend.core.worker_service import loop_mgr            # singleton LoopManager
from backend.core.providers.infra_providers import get_postgres_session, get_mongo_db
from backend.core.email.email_template_service import EmailTemplateService
from backend.core.email.email_sender_service import EmailSenderService
from backend.data_access.postgres.hr.hr_user_repository import HRUserRepository
from backend.utils.string_utils import extract_name_from_email

# TasksRepository (task-state store)
from backend.data_access.mongo.task.tasks_repository import TasksRepository
from backend.data_access.mongo.gridfs_loader import GridFSLoader

# ---------- Async business coroutine ----------
async def send_invitations_async(
    emails: List[str],
    job_title: str,
    parsed_date: datetime,
    interview_link: str,
    company_field: Optional[str],
    sender_service: EmailSenderService,
    template_service: EmailTemplateService
) -> Dict[str, Any]:
    """
    Coroutine that does the DB lookup, templating and sending emails.
    This coroutine assumes parsed_date and company_field are prepared.
    """
    sent = 0
    failed = 0
    failures = []

    # send sequentially; could be parallelized with throttling if needed
    for email in emails:
        try:
            candidate_name = extract_name_from_email(email)

            html_body = template_service.render_invitation(
                candidate_name=candidate_name,
                job_title=job_title,
                interview_date=parsed_date,
                interview_link=interview_link,
                company_field=company_field
            )

            subject = f"Interview Invitation - {job_title}"

            # Blocking send_email -> run in threadpool to avoid blocking event loop
            await asyncio.to_thread(sender_service.send_email, email, subject, html_body)

            sent += 1

        except Exception as exc:
            failed += 1
            failures.append({"email": email, "error": str(exc), "trace": traceback.format_exc()})
            # continue sending remaining emails

    return {"sent": sent, "failed": failed, "failures": failures, "scheduled_for": parsed_date.isoformat()}


# ---------- Sync wrapper called by RQ (expects job_id) ----------
def send_invitation_job(job_id: str):
    """
    Wrapper for RQ: fetch task doc from TasksRepository, load payload from GridFS,
    run async processing on loop_mgr, and update task status accordingly.
    """
    # repo uses infra provider's mongo DB (sync accessor returns AsyncIOMotorDatabase but repo methods are async)
    repo = TasksRepository(db=get_mongo_db())

    # 1) atomic pick -> mark as processing
    try:
        task = loop_mgr.run_coro_sync(repo.get_and_mark_processing(job_id), timeout=int(os.getenv("TASK_REPO_TIMEOUT", "1200")))
    except Exception as exc:
        # DB error: rethrow so RQ can retry invoking the wrapper or alert
        raise

    if not task:
        # Nothing to do (already processing/done/missing)
        return

    # Optional: emit metric jobs_processing_current.inc()

    payload_ref = task.get("payload_ref")
    if not payload_ref:
        # malformed task: mark failed
        loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason="missing_payload_ref"), timeout=1200)
        return

    # 2) load payload from GridFS (async) via loop_mgr
    try:
        payload = loop_mgr.run_coro_sync(GridFSLoader.load_json_from_gridfs_async(payload_ref), timeout=int(os.getenv("PAYLOAD_LOAD_TIMEOUT", "400")))
    except Exception as exc:
        # increment attempts and possibly DLQ
        attempts = loop_mgr.run_coro_sync(repo.increment_attempts(job_id), timeout=5)
        if attempts >= task.get("max_attempts", 5):
            loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason=f"payload_load_error: {str(exc)}"), timeout=5)
        raise

    # payload expected structure example:
    # { "emails": [...], "job_title": "...", "raw_date": "...", "interview_link": "...", "hr_id": 123 }
    emails = payload.get("emails", [])
    job_title = payload.get("job_title", "")
    raw_date = payload.get("raw_date")
    interview_link = payload.get("interview_link", "")
    hr_id = payload.get("hr_id", task.get("owner"))  # fallback to task.owner if present

    # 3) prepare context for async coroutine
    # parse date safely
    parsed_date = None
    if isinstance(raw_date, str):
        try:
            parsed_date = datetime.strptime(raw_date.strip(), "%Y-%m-%d")
        except Exception:
            parsed_date = None
    if not isinstance(parsed_date, datetime):
        parsed_date = datetime.utcnow() + timedelta(days=2)

    # fetch company_field via Postgres (async)
    try:
        company_field = None
        # reuse existing async providers on background loop
        async def _fetch_company_field():
            async for session in get_postgres_session():
                hr_repo = HRUserRepository(session)
                return await hr_repo.get_company_field_by_hr_id(hr_id)
            return None

        company_field = loop_mgr.run_coro_sync(_fetch_company_field(), timeout=int(os.getenv("DB_FETCH_TIMEOUT", "10")))
    except Exception:
        company_field = None  # continue, not fatal

    # init services (consider making them process-singleton if heavy)
    template_service = EmailTemplateService()
    sender_service = EmailSenderService()

    # 4) run the main coroutine on background loop
    start_ts = time.time()
    try:
        result = loop_mgr.run_coro_sync(
            send_invitations_async(emails, job_title, parsed_date, interview_link, company_field, sender_service, template_service),
            timeout=int(os.getenv("SEND_INVITATION_PROCESS_TIMEOUT", "1200"))
        )

        # mark succeeded
        loop_mgr.run_coro_sync(repo.mark_succeeded(job_id, result_ref=None), timeout=5)

        # emit metric job_succeeded, observe duration
        return result

    except Exception as exc:
        # increment attempts and possibly DLQ
        attempts = loop_mgr.run_coro_sync(repo.increment_attempts(job_id), timeout=5)
        if attempts >= task.get("max_attempts", 5):
            loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason=str(exc)), timeout=5)
        # emit metric job_failed
        raise

    finally:
        duration = time.time() - start_ts
        # emit metric job_duration_seconds.observe(duration)
