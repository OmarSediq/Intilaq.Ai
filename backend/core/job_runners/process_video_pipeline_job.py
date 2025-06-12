import asyncio
import io
import uuid

from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.core.providers.infra_providers import get_mongo_client_raw
from backend.core.providers.video_providers.video_provider import (
    get_video_compressor_service,
    get_audio_extractor_service
)
from backend.core.providers.ai_providers.whisper_provider import get_whisper_sender_service
from backend.core.providers.ai_providers.gemini_provider import get_gemini_ai_service
from backend.core.providers.data_access_providers.hr_providers.hr_gridfs_storage_repository_provider import (
    get_hr_gridfs_storage_service_async
)
from backend.domain_services.video.video_metadata_service import VideoMetadataService


async def process(video_id: str):
    mongo_client = await get_mongo_client_raw()
    db = mongo_client["hr_db"]
    answer_repo = HRAnswerRepository(db)

    gridfs_storage = await get_hr_gridfs_storage_service_async()
    video_compressor = get_video_compressor_service()
    audio_extractor = get_audio_extractor_service()
    whisper_sender = get_whisper_sender_service()
    gemini_service = get_gemini_ai_service()
    video_metadata = VideoMetadataService()

    answer_record = await answer_repo.get_session_by_video_id(video_id)
    if not answer_record:
        print(f"[ERROR] No answer found for video_id: {video_id}")
        return

    interview_token = answer_record["interview_token"]
    answers = answer_record.get("answers", [])
    target_index = next(
        (i for i, a in enumerate(answers) if str(a.get("video_file_id")) == video_id),
        None
    )
    if target_index is None:
        print(f"[ERROR] No matching answer in answers[] for video_id: {video_id}")
        return

    video_bytes = await gridfs_storage.get_video_by_file_id(video_id)
    compressed_video = await video_compressor.compress_video(video_bytes)

    compressed_video_filename = f"compressed_{uuid.uuid4().hex}.webm"
    compressed_video_id = await gridfs_storage.save_video(
        filename=compressed_video_filename,
        file_stream=compressed_video
    )

    await answer_repo.update_answer_by_index(
        interview_token, target_index,
        {"video_file_id": str(compressed_video_id)}
    )

    audio_bytes = await audio_extractor.extract_audio(compressed_video)
    audio_filename = f"audio_{uuid.uuid4().hex}.webm"
    audio_file_id = await gridfs_storage.save_audio(audio_filename, audio_bytes)

    await answer_repo.update_answer_by_index(
        interview_token, target_index,
        {"audio_file_id": str(audio_file_id)}
    )

    transcript = await whisper_sender.send_audio_for_transcription(audio_bytes)
    await answer_repo.update_answer_by_index(
        interview_token, target_index,
        {"transcript": transcript}
    )

    question_doc = await db["hr_interview_questions"].find_one({"interview_token": interview_token})
    if not question_doc:
        print(f"[ERROR] No hr_interview_questions document found for interview_token: {interview_token}")
        return

    questions = question_doc.get("questions", [])
    if target_index >= len(questions):
        print(f"[ERROR] No question found at index {target_index} in hr_interview_questions")
        return

    question_data = questions[target_index]
    time_limit = question_data.get("time_limit")  #
    ideal_answer = question_data.get("ideal_answer", "").strip()

    if not ideal_answer:
        print(f"[WARNING] No ideal_answer provided for index {target_index}")
        return

    transcribed_text = transcript.get("text", "").strip()
    score = gemini_service.analyze_similarity_score(transcribed_text, ideal_answer)

    duration = video_metadata.get_duration(compressed_video)

    await answer_repo.update_answer_by_index(
        interview_token,
        target_index,
        {
            "score": score,
            "video_duration": duration,
            "question_time_limit": time_limit,
        }
    )

    print(f"[DONE] Finished processing video_id: {video_id}, score={score}, duration={duration}, time_limit={time_limit}")


def run(video_id: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process(video_id))
    finally:
        loop.close()
