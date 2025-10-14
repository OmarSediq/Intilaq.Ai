# backend/core/job_processors/evaluate_text_answer_job.py
import os
import time
import traceback
import asyncio
from typing import Optional, Dict, Any

from backend.core.worker_service import loop_mgr
from backend.core.providers.infra_providers import get_mongo_client_raw, get_mongo_db
from backend.data_access.mongo.task.tasks_repository import TasksRepository
from backend.data_access.mongo.gridfs_loader import load_json_from_gridfs_async

from backend.domain_services.hr_services.hr_summary_service import HRUserSummaryService
from backend.data_access.mongo.hr.hr_summary_repository import HRSummaryRepository
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.core.providers.ai_providers.gemini_provider import get_gemini_ai_service

# ------------------ Async business logic (kept mostly as you had) ------------------
async def evaluate(interview_token: str, user_email: str, index: int) -> Optional[Dict[str, Any]]:

    mongo_client = await get_mongo_client_raw()
    db = mongo_client["hr_db"]
    answer_repo = HRAnswerRepository(db)
    summary_repo = HRSummaryRepository(db)
    interview_repo = HRInterviewRepository(db)
    summary_service = HRUserSummaryService(
        answer_repo=answer_repo,
        interview_repo=interview_repo,
        summary_repo=summary_repo
    )
    gemini_service = get_gemini_ai_service()

    answer_record = await answer_repo.get_session_by_token_and_email(interview_token, user_email)
    if not answer_record:
        # nothing to do
        return None

    answers = answer_record.get("answers", [])
    if index >= len(answers):
        return None

    user_answer_text_raw = answers[index].get("answer_text")
    if not user_answer_text_raw or not isinstance(user_answer_text_raw, str):
        return None

    user_answer_text = user_answer_text_raw.strip()
    if not user_answer_text:
        return None

    question_doc = await db["hr_interview_questions"].find_one({"interview_token": interview_token})
    if not question_doc:
        return None

    questions = question_doc.get("questions", [])
    if index >= len(questions):
        return None

    ideal_answer = questions[index].get("ideal_answer", "").strip()
    if not ideal_answer:
        return None

    score = gemini_service.analyze_similarity_score(user_answer_text, ideal_answer)

    await answer_repo.update_answer_by_index(
        interview_token, user_email, index,
        {"score": score}
    )

    total_questions = len(questions)
    await _maybe_set_overall(answer_repo, interview_token, user_email, total_questions)
    await summary_service.list_participants(interview_token)

    return {"score": score, "interview_token": interview_token, "user_email": user_email, "index": index}


async def _maybe_set_overall(answer_repo, interview_token, user_email,
                             total_questions: int):
    doc = await answer_repo.get_session_by_token_and_email(
        interview_token, user_email)

    scored = [a.get("score") for a in doc["answers"] if a.get("score") is not None]
    if len(scored) != total_questions:
        return

    overall = round(sum(scored) / (total_questions * 10) * 100, 2)
    await answer_repo.set_overall_score(interview_token, user_email, overall)


# ------------------ Sync wrapper for RQ (uses TasksRepository + loop_mgr) ------------------
def evaluate_job_wrapper(job_id: str):
    """
    Sync wrapper expected by RQ. job_id is the TasksRepository document _id (string).
    Steps:
      - atomic pick (get_and_mark_processing)
      - load payload (via GridFS async loader)
      - extract interview_token, user_email, index
      - run evaluate(...) coroutine on background loop via loop_mgr.run_coro_sync
      - update task state (succeeded/failed) and attempts
    """
    # configurable timeouts via env
    TASK_REPO_TIMEOUT = int(os.getenv("TASK_REPO_TIMEOUT", "1200"))
    PAYLOAD_LOAD_TIMEOUT = int(os.getenv("PAYLOAD_LOAD_TIMEOUT", "1200"))
    PROCESS_TIMEOUT = int(os.getenv("EVALUATE_PROCESS_TIMEOUT", "1200"))

    repo = TasksRepository(db=get_mongo_db())

    # 1) atomic pick
    try:
        task = loop_mgr.run_coro_sync(repo.get_and_mark_processing(job_id), timeout=TASK_REPO_TIMEOUT)
    except Exception as exc:
        # DB access error -> rethrow so RQ may retry wrapper
        raise

    if not task:
        # no task to process (already processing/done/missing)
        return

    # 2) load payload (async GridFS) via loop_mgr
    payload_ref = task.get("payload_ref")
    if not payload_ref:
        loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason="missing_payload_ref"), timeout=5)
        return

    try:
        payload = loop_mgr.run_coro_sync(load_json_from_gridfs_async(payload_ref), timeout=PAYLOAD_LOAD_TIMEOUT)
    except Exception as exc:
        # increment attempts and possibly DLQ
        attempts = loop_mgr.run_coro_sync(repo.increment_attempts(job_id), timeout=5)
        if attempts >= task.get("max_attempts", 5):
            loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason=f"payload_load_error: {str(exc)}"), timeout=5)
        raise

    # payload expected to contain minimal fields: {"interview_token":"...", "user_email":"...", "index": 0}
    interview_token = payload.get("interview_token")
    user_email = payload.get("user_email")
    index = payload.get("index")

    if not (interview_token and user_email and isinstance(index, int)):
        loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason="invalid_payload_fields"), timeout=5)
        return

    # 3) run evaluate coroutine on background loop
    start_ts = time.time()
    try:
        result = loop_mgr.run_coro_sync(evaluate(interview_token, user_email, index), timeout=PROCESS_TIMEOUT)
        # mark succeeded
        loop_mgr.run_coro_sync(repo.mark_succeeded(job_id, result_ref=None), timeout=5)
        return result

    except Exception as exc:
        # increment attempts and maybe move to DLQ if too many attempts
        attempts = loop_mgr.run_coro_sync(repo.increment_attempts(job_id), timeout=5)
        if attempts >= task.get("max_attempts", 5):
            loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason=str(exc)), timeout=5)
        # re-raise to let RQ handle retry/backoff policy if configured
        raise

    finally:
        duration = time.time() - start_ts
        # here you should emit metrics: job_duration_seconds.observe(duration), job_failed_total.inc(), etc.
