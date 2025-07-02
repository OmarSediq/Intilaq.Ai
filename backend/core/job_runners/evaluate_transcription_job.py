import asyncio
from backend.domain_services.hr_services.hr_summary_service import HRUserSummaryService
from backend.data_access.mongo.hr.hr_summary_repository import HRSummaryRepository
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository

from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.core.providers.infra_providers import get_mongo_client_raw
from backend.core.providers.ai_providers.gemini_provider import get_gemini_ai_service


async def evaluate(interview_token: str, user_email: str, index: int):
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
        print(f"[ERROR] No session found for token: {interview_token} and email: {user_email}")
        return

    answers = answer_record.get("answers", [])
    if index >= len(answers):
        print(f"[ERROR] No answer found at index {index}")
        return

    user_answer_text_raw = answers[index].get("answer_text")
    if not user_answer_text_raw or not isinstance(user_answer_text_raw, str):
        print(f"[ERROR] answer_text is invalid at index {index}")
        return

    user_answer_text = user_answer_text_raw.strip()
    if not user_answer_text:
        print(f"[ERROR] answer_text is empty at index {index}")
        return

    question_doc = await db["hr_interview_questions"].find_one({"interview_token": interview_token})
    if not question_doc:
        print(f"[ERROR] No hr_interview_questions found for token: {interview_token}")
        return

    questions = question_doc.get("questions", [])
    if index >= len(questions):
        print(f"[ERROR] No question found at index {index}")
        return

    ideal_answer = questions[index].get("ideal_answer", "").strip()
    if not ideal_answer:
        print(f"[WARNING] No ideal_answer at index {index}")
        return

    score = gemini_service.analyze_similarity_score(user_answer_text, ideal_answer)
    print("Updating score:", score)

    await answer_repo.update_answer_by_index(
        interview_token, user_email, index,
        {"score": score}
    )

    print(f"[DONE] Score updated for text response at index={index}, score={score}")

    total_questions = len(questions)
    await _maybe_set_overall(answer_repo, interview_token, user_email, total_questions)
    await summary_service.list_participants(interview_token)

def run(interview_token: str, user_email: str, index: int):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(evaluate(interview_token, user_email, index))
    finally:
        loop.close()



async def _maybe_set_overall(answer_repo, interview_token, user_email,
                             total_questions: int):
    doc = await answer_repo.get_session_by_token_and_email(
        interview_token, user_email)

    scored = [a.get("score") for a in doc["answers"] if a.get("score") is not None]
    if len(scored) != total_questions:
        return

    overall = round(sum(scored) / (total_questions * 10) * 100, 2)
    await answer_repo.set_overall_score(interview_token, user_email, overall)
