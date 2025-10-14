# backend/core/job_processors/process_video_job.py
import os
import traceback
import time
import logging
from typing import Optional, Dict, Any, Union
from bson import ObjectId
import inspect
import asyncio

from backend.data_access.mongo.gridfs_loader import GridFSLoader
from backend.core.worker_service import loop_mgr
from backend.core.providers.infra_providers import get_mongo_client_raw
from backend.data_access.mongo.task.tasks_repository import TasksRepository
from backend.core.providers.data_access_providers.hr_providers.hr_gridfs_storage_repository_provider import (
    get_hr_gridfs_storage_service_async,
)
from backend.core.providers.video_providers.video_provider import (
    get_video_compressor_service,
    get_audio_extractor_service,
)
from backend.core.providers.ai_providers.whisper_provider import get_whisper_sender_service
from backend.core.providers.ai_providers.gemini_provider import get_gemini_ai_service

from backend.domain_services.hr_services.hr_summary_service import HRUserSummaryService
from backend.data_access.mongo.hr.hr_summary_repository import HRSummaryRepository
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.domain_services.video.video_metadata_service import VideoMetadataService

logger = logging.getLogger("video_pipeline")
logger.setLevel(os.getenv("VIDEO_PIPELINE_LOG_LEVEL", "INFO"))


def uuid4_hex() -> str:
    import uuid
    return uuid.uuid4().hex


def _normalize_payload_ref_to_objectid(payload_ref: Union[str, ObjectId]) -> ObjectId:
    if payload_ref is None:
        raise ValueError("payload_ref is None")
    if isinstance(payload_ref, ObjectId):
        return payload_ref
    if isinstance(payload_ref, str):
        ref = payload_ref.strip()
        if ref.startswith("gridfs://"):
            ref = ref.split("://", 1)[1]
        try:
            return ObjectId(ref)
        except Exception as exc:
            raise ValueError(f"invalid payload_ref for ObjectId: {payload_ref}") from exc
    raise ValueError(f"unsupported payload_ref type: {type(payload_ref)}")


async def _maybe_await(value):
    """
    Helper: if 'value' is awaitable -> await it, else return directly.
    This allows flexibility if some providers are async or sync.
    """
    if inspect.isawaitable(value):
        return await value
    return value


# ---- MAIN async processor ----
async def process(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Async pipeline processing for a single video id.
    This function runs inside an event loop (either the application's loop or the worker's background loop).
    """
    # client getter is sync (returns AsyncIOMotorClient)
    client = get_mongo_client_raw()
    db = client["hr_db"]
    logger.info(
        "process started for video_id=%s on db=%s client_id=%s",
        video_id,
        getattr(db, "name", None),
        id(client),
    )

    # instantiate repositories/services (all accept AsyncIOMotorDatabase)
    answer_repo = HRAnswerRepository(db)
    summary_repo = HRSummaryRepository(db)
    interview_repo = HRInterviewRepository(db)
    summary_service = HRUserSummaryService(
        answer_repo=answer_repo, interview_repo=interview_repo, summary_repo=summary_repo
    )

    # GridFS provider: allow provider to be async or sync
    gridfs_candidate = get_hr_gridfs_storage_service_async()
    gridfs_storage = await _maybe_await(gridfs_candidate)

    # other helpers (assumed sync factories returning objects possibly with async methods)
    video_compressor = get_video_compressor_service()
    audio_extractor = get_audio_extractor_service()
    whisper_sender = get_whisper_sender_service()
    gemini_service = get_gemini_ai_service()
    video_metadata = VideoMetadataService()

    # ---- begin pipeline ----
    answer_record = await answer_repo.get_session_by_video_id(video_id)
    if not answer_record:
        logger.warning("no answer_record found for video_id=%s", video_id)
        return None

    interview_token = answer_record.get("interview_token")
    user_email = answer_record.get("user_email")
    answers = answer_record.get("answers", []) or []
    target_index = next(
        (i for i, a in enumerate(answers) if str(a.get("video_file_id")) == str(video_id)),
        None,
    )
    if target_index is None:
        logger.warning("video_id %s not found in answers for interview %s", video_id, interview_token)
        return None

    # load video bytes from GridFS (async method on the storage service)
    logger.info("loading video from GridFS: video_id=%s", video_id)
    video_bytes = await gridfs_storage.get_video_by_file_id(video_id)
    logger.info("loaded video bytes: %s for video_id=%s", len(video_bytes) if video_bytes else None, video_id)
    if not video_bytes:
        logger.warning("no video bytes returned for video_id=%s", video_id)
        return None

    # compress video
    try:
        compressed_video = await video_compressor.compress_video(video_bytes)
        logger.info("video compressed for video_id=%s", video_id)
    except Exception as exc:
        logger.exception("video compression failed for video_id=%s: %s", video_id, exc)
        raise

    compressed_video_filename = f"compressed_{uuid4_hex()}.webm"
    compressed_video_id = await gridfs_storage.save_video(filename=compressed_video_filename, file_stream=compressed_video)

    await answer_repo.update_answer_by_index(
        interview_token, user_email, target_index, {"video_file_id": str(compressed_video_id)}
    )

    # extract audio
    try:
        audio_bytes = await audio_extractor.extract_audio(compressed_video)
        logger.info("extracted audio bytes length=%s for video_id=%s", len(audio_bytes) if audio_bytes else None, video_id)
    except Exception as exc:
        logger.exception("audio extraction failed for video_id=%s: %s", video_id, exc)
        raise

    audio_filename = f"audio_{uuid4_hex()}.webm"
    audio_file_id = await gridfs_storage.save_audio(audio_filename, audio_bytes)
    await answer_repo.update_answer_by_index(interview_token, user_email, target_index, {"audio_file_id": str(audio_file_id)})

    # transcribe (whisper)
    try:
        logger.info("sending audio to whisper for video_id=%s", video_id)
        transcript = await whisper_sender.send_audio_for_transcription(audio_bytes)
        logger.info("whisper returned transcript type=%s for video_id=%s", type(transcript), video_id)
    except Exception as exc:
        logger.exception("whisper transcription failed for video_id=%s: %s", video_id, exc)
        raise

    await answer_repo.update_answer_by_index(interview_token, user_email, target_index, {"transcript": transcript})
    logger.info("saved transcript for interview=%s user=%s index=%s", interview_token, user_email, target_index)

    # fetch question doc & score
    question_doc = await db["hr_interview_questions"].find_one({"interview_token": interview_token})
    if not question_doc:
        logger.warning("no question_doc for interview_token=%s", interview_token)
        return None

    questions = question_doc.get("questions", []) or []
    if target_index >= len(questions):
        logger.warning("target_index %s out of range for interview_token=%s", target_index, interview_token)
        return None

    question_data = questions[target_index]
    time_limit = question_data.get("time_limit")
    ideal_answer = (question_data.get("ideal_answer") or "").strip()
    if not ideal_answer:
        logger.warning("no ideal_answer for interview_token=%s index=%s", interview_token, target_index)
        return None

    transcribed_text = (transcript.get("text") if isinstance(transcript, dict) else str(transcript)).strip()
    try:
        score = gemini_service.analyze_similarity_score(transcribed_text, ideal_answer)
        logger.info("gemini returned score=%s for interview=%s user=%s index=%s", score, interview_token, user_email, target_index)
    except Exception as exc:
        logger.exception("gemini analyze failed for video_id=%s: %s", video_id, exc)
        raise

    duration = video_metadata.get_duration(compressed_video)
    await answer_repo.update_answer_by_index(
        interview_token,
        user_email,
        target_index,
        {"score": score, "video_duration": duration, "question_time_limit": time_limit},
    )
    logger.info("updated answer with score & duration for interview=%s user=%s index=%s", interview_token, user_email, target_index)

    total_questions = len(questions)
    await _maybe_set_overall(answer_repo, interview_token, user_email, total_questions)
    await summary_service.list_participants(interview_token)

    return {"score": score, "duration": duration, "video_id": str(compressed_video_id)}


async def _maybe_set_overall(answer_repo, interview_token, user_email, total_questions: int):
    doc = await answer_repo.get_session_by_token_and_email(interview_token, user_email)
    scored = [a.get("score") for a in doc["answers"] if a.get("score") is not None]
    if len(scored) != total_questions:
        return
    overall = round(sum(scored) / (total_questions * 10) * 100, 2)
    await answer_repo.set_overall_score(interview_token, user_email, overall)


# ---- sync wrapper for RQ ----
def process_job_wrapper(job_id: str):
    """
    Sync wrapper called by RQ worker process.
    Uses loop_mgr to run coroutines from the background loop.
    """
    if not loop_mgr.is_ready():
        try:
            loop_mgr.start(wait_ready=True, timeout=10)
        except Exception as exc:
            raise RuntimeError(f"failed to start loop_mgr in worker child: {exc}")

    TASK_REPO_TIMEOUT = int(os.getenv("TASK_REPO_TIMEOUT", "1200"))
    PAYLOAD_LOAD_TIMEOUT = int(os.getenv("PAYLOAD_LOAD_TIMEOUT", "1200"))
    PROCESS_TIMEOUT = int(os.getenv("VIDEO_PROCESS_TIMEOUT", "1800"))
    MAX_ATTEMPTS_DEFAULT = int(os.getenv("TASK_MAX_ATTEMPTS", "5"))

    client = get_mongo_client_raw()
    db = client["hr_db"]
    repo = TasksRepository(db=db)

    # 1) pick task atomically
    try:
        task = loop_mgr.run_coro_sync(repo.get_and_mark_processing(job_id), timeout=TASK_REPO_TIMEOUT)
    except Exception as exc:
        logger.exception("failed to get_and_mark_processing for job=%s: %s", job_id, exc)
        raise

    if not task:
        logger.info("no task returned (already processing/done) for job=%s", job_id)
        return

    payload_ref_raw = task.get("payload_ref")
    if not payload_ref_raw:
        loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason="missing_payload_ref"), timeout=5)
        logger.error("missing payload_ref for job=%s", job_id)
        return

    try:
        payload_oid = _normalize_payload_ref_to_objectid(payload_ref_raw)
    except Exception as exc:
        logger.exception("payload_ref normalization failed for job=%s payload_ref=%s: %s", job_id, payload_ref_raw, exc)
        loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason=f"payload_normalization_error: {exc}"), timeout=5)
        raise

    logger.info("loading payload for job=%s payload_oid=%s", job_id, payload_oid)

    # Load payload JSON from GridFS (gridfs_loader.get_json_by_file_id is async)
    
    try:
        loader = GridFSLoader()
        payload = loop_mgr.run_coro_sync(loader.load_json_from_gridfs_async(payload_oid))   
    except Exception as exc:
        logger.exception("payload load failed for job=%s payload_oid=%s: %s", job_id, payload_oid, exc)
        attempts = loop_mgr.run_coro_sync(repo.increment_attempts(job_id), timeout=5)
        max_attempts = task.get("max_attempts", MAX_ATTEMPTS_DEFAULT)
        if attempts >= max_attempts:
            loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason=f"payload_load_error: {str(exc)}"), timeout=5)
        raise

    if not isinstance(payload, dict):
        loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason="invalid_payload_type"), timeout=5)
        logger.error("invalid payload type for job=%s payload=%s", job_id, payload)
        return

    video_file_id = payload.get("video_file_id")
    if not video_file_id:
        loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason="no_video_file_id"), timeout=5)
        logger.error("no video_file_id in payload for job=%s payload=%s", job_id, payload)
        return

    # run the async pipeline (process) on the background loop
    start_ts = time.time()
    try:
        result = loop_mgr.run_coro_sync(process(video_file_id), timeout=PROCESS_TIMEOUT)
        loop_mgr.run_coro_sync(repo.mark_succeeded(job_id, result_ref=None), timeout=5)
        logger.info("job %s completed successfully, result=%s", job_id, result)
        return result
    except Exception as exc:
        tb = traceback.format_exc()
        attempts = loop_mgr.run_coro_sync(repo.increment_attempts(job_id), timeout=5)
        max_attempts = task.get("max_attempts", MAX_ATTEMPTS_DEFAULT)
        if attempts >= max_attempts:
            loop_mgr.run_coro_sync(repo.mark_failed(job_id, reason=str(exc)), timeout=5)
        logger.exception("job %s raised exception: %s\n%s", job_id, exc, tb)
        raise
    finally:
        duration = time.time() - start_ts
        # emit metrics if desired
        logger.debug("job %s duration=%.2f", job_id, duration)
