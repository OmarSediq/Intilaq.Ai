from fastapi import APIRouter, HTTPException ,UploadFile, File,Depends 
from app.services.mongo_services import get_mongo_client,insert_question_session,find_session_by_session_id ,insert_user_answer,update_answer_feedback,find_latest_answer,get_all_answers_with_scores 
from app.services.redis_services import redis_client , set_current_question_index,get_current_question_index,add_completed_question,set_session_status,get_user_session_ids,add_user_session_id
from app.services.ai_services import generate_interview_questions,generate_best_model_answer,generate_feedback , analyze_answer
from app.api.auth_api.auth.routes_auth import get_current_user
from app.utils.response_schemas import error_response , success_response
import asyncio
import random
import os 
import httpx
from datetime import datetime , timezone
from app.schemas.interview import JobData
router = APIRouter()
       

WHISPER_SERVICE_URL = os.getenv("WHISPER_SERVICE_URL", "http://whisper-container:5001/transcribe")

async def get_db():
    client = await get_mongo_client()
    if client is None: 
        raise HTTPException(status_code=500, detail="MongoDB connection is not available")
    return client["interview_db"]


# async def get_interview_session_data(user=Depends(get_current_user), db=Depends(get_db)):
#     session_id = await redis_client.get(f"user:{user['user_id']}:session")

#     if session_id:
#         session_id = int(session_id)  
#     else:
#         session = await db["questions"].find_one({"user_id": user["user_id"]})
#         if session:
#             session_id = int(session["session_id"])  
#             await redis_client.set(f"user:{user['user_id']}:session", session_id)  
#         else:
#             raise HTTPException(status_code=404, detail="No active session found")

#     async with redis_client.pipeline() as pipe:
#         pipe.get(f"session:{session_id}:current_question")
#         pipe.smembers(f"session:{session_id}:completed_questions")
#         results = await pipe.execute()

#     if results[0] is None:
#         session = await db["questions"].find_one({"session_id": session_id}, {"current_question_index": 1})
#         current_question_index = session["current_question_index"] if session else 0
#         await redis_client.set(f"session:{session_id}:current_question", current_question_index)
#     else:
#         current_question_index = int(results[0])

#     completed_questions = list(map(int, results[1])) if results[1] else []

#     print(f"🔍 DEBUG: session_id={session_id}, current_question_index={current_question_index}")

#     return {
#         "session_id": session_id,  
#         "user_id": user["user_id"],
#         "current_question_index": current_question_index,
#         "completed_questions": completed_questions
#     }

async def validate_and_sync_session(session_id: int, user_id: str) -> bool:
    session = await find_session_by_session_id(session_id, user_id)
    if not session:
        return False

    redis_session_ids = await get_user_session_ids(user_id)

    if session_id not in redis_session_ids:
        await add_user_session_id(user_id, session_id)

    return True


    
@router.get("/api/sessions/job-titles", tags=["Reference Data"])
async def get_job_titles(db=Depends(get_db)):
    try:
        job_titles_collection = db["job_titles"]
        titles = await job_titles_collection.distinct("title")
        return success_response(code=200, data={"job_titles": titles})
    except Exception as e:
        return error_response(code=500, error_message=f"Error fetching job titles: {str(e)}")

@router.get("/api/sessions/job-levels", tags=["Reference Data"])
async def get_job_levels(db=Depends(get_db)):
    try:
        job_levels_collection = db["job_levels"]
        levels = await job_levels_collection.distinct("level")
        return success_response(code=200, data={"job_levels": levels})
    except Exception as e:
        return error_response(code=500, error_message=f"Error fetching job levels: {str(e)}")



@router.post("/api/sessions/", tags=["Interview Sessions"])
async def create_interview_session(
    job_data: JobData,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        ai_questions = await generate_interview_questions(job_data.job_title, job_data.level, job_data.description)
        if not ai_questions:
            return error_response(code=400, error_message="No questions generated")

        questions_list = [q.strip() for q in ai_questions.split("\n") if q.strip()]
        session_id = random.randint(100000, 999999)

        best_model_answers = await asyncio.gather(
            *[generate_best_model_answer(q) for q in questions_list]
        )

        questions_with_answers = [
            {"question_index": idx, "question": q, "best_model_answer": a}
            for idx, (q, a) in enumerate(zip(questions_list, best_model_answers))
        ]

        session_data = {
            "session_id": session_id,
            "user_id": user["user_id"],
            "job_title": job_data.job_title,
            "level": job_data.level,
            "questions": questions_with_answers,
            "current_question_index": 0,
            "created_at": datetime.now(timezone.utc)
        }

        await insert_question_session(session_data)
        await add_user_session_id(user["user_id"], session_id)

        await set_current_question_index(session_id, 0)

        return success_response(code=201, data={"message": "Interview session created", "session_id": session_id})
    
    except Exception as e:
        return error_response(code=500, error_message=f"Error creating interview session: {str(e)}")


@router.get("/api/sessions/{session_id}/questions")
async def get_questions(session_id: int, user=Depends(get_current_user)):
    is_valid = await validate_and_sync_session(session_id, user["user_id"])
    if not is_valid:
        return error_response(code=404, error_message="Session not found or unauthorized")

    session = await find_session_by_session_id(session_id, user["user_id"])
    questions_only = [q["question"] for q in session["questions"]]
    return success_response(code=200, data={"session_id": session_id, "questions": questions_only})


@router.get("/api/sessions/{session_id}/questions/next")
async def get_next_question(session_id: int, user=Depends(get_current_user)):
    is_valid = await validate_and_sync_session(session_id, user["user_id"])
    if not is_valid:
        return error_response(code=404, error_message="Session not found or unauthorized")

    session = await find_session_by_session_id(session_id, user["user_id"])
    current_index = await get_current_question_index(session_id)
    questions = session["questions"]

    if current_index >= len(questions):
        return success_response(code=200, data={"message": "No more questions available."})

    question = questions[current_index]
    # await set_current_question_index(session_id, current_index + 1)

    return success_response(code=200, data={
        "question": question["question"],
        "question_index": current_index
    })


@router.post("/api/sessions/{session_id}/answers")
async def submit_answer(session_id: int, file: UploadFile = File(...), user=Depends(get_current_user)):
    is_valid = await validate_and_sync_session(session_id, user["user_id"])
    if not is_valid:
        return error_response(code=404, error_message="Session not found or unauthorized")

    session = await find_session_by_session_id(session_id, user["user_id"])
    current_index = await get_current_question_index(session_id)

    if current_index >= len(session["questions"]):
        return error_response(code=400, error_message="No more questions remaining")

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            files = {"file": (file.filename, file.file.read(), file.content_type)}
            response = await client.post(WHISPER_SERVICE_URL, files=files)

        if response.status_code != 200:
            return error_response(code=500, error_message=f"Whisper API error: {response.text}")

        transcribed_text = response.json().get("text", "").strip()
        if not transcribed_text:
            return error_response(code=400, error_message="Transcription failed, no text found.")

        await insert_user_answer({
            "session_id": session_id,
            "user_id": user["user_id"],
            "question_index": current_index,
            "answer_text": transcribed_text,
            "timestamp": datetime.now(timezone.utc)
        })

        await add_completed_question(session_id, current_index)
        await set_current_question_index(session_id, current_index + 1)  

        return success_response(code=200, data={
            "message": "Answer submitted successfully",
            "question_index": current_index,
            "transcribed_text": transcribed_text
        })

    except Exception as e:
        return error_response(code=500, error_message=f"Speech-to-Text failed: {str(e)}")


@router.get("/api/sessions/{session_id}/answers/{question_index}/feedback")
async def get_feedback(session_id: int, question_index: int, user=Depends(get_current_user)):
    is_valid = await validate_and_sync_session(session_id, user["user_id"])
    if not is_valid:
        return error_response(code=404, error_message="Session not found or unauthorized")

    latest_answer = await find_latest_answer(session_id, user["user_id"])
    if not latest_answer:
        return error_response(code=404, error_message="User answer not found")

    session = await find_session_by_session_id(session_id, user["user_id"])
    question_data = session["questions"][question_index]
    user_answer = latest_answer["answer_text"]
    ideal_answer = question_data.get("best_model_answer", "N/A")
    question_text = question_data["question"]

    feedback = generate_feedback(user_answer, question_text, ideal_answer)
    similarity_score = analyze_answer(user_answer, ideal_answer)

    await update_answer_feedback(session_id, user["user_id"], question_index, {
        "feedback": feedback,
        "similarity_score": similarity_score
    })

    return success_response(code=200, data={
        "question": question_text,
        "user_answer": user_answer,
        "ideal_answer": ideal_answer,
        **feedback,
        "similarity_score": similarity_score
    })


@router.post("/api/sessions/{session_id}/start")
async def start_session(session_id: int, user=Depends(get_current_user)):
    is_valid = await validate_and_sync_session(session_id, user["user_id"])
    if not is_valid:
        return error_response(code=404, error_message="Session not found or unauthorized")

    await set_session_status(session_id, "active")
    await set_current_question_index(session_id, 0)

    return success_response(code=200, data={"message": "Session started successfully", "session_id": session_id})


@router.post("/api/sessions/{session_id}/end")
async def end_session(session_id: int, user=Depends(get_current_user), db=Depends(get_db)):
    is_valid = await validate_and_sync_session(session_id, user["user_id"])
    if not is_valid:
        return error_response(code=404, error_message="Session not found or unauthorized")

    answers = await get_all_answers_with_scores(session_id, user["user_id"])
    if not answers:
        return error_response(code=404, error_message="No answers with scores found for this session")

    scores = [ans.get("similarity_score", 0) for ans in answers]
    if not scores:
        return error_response(code=404, error_message="No similarity scores found")

    total_score = sum(scores)
    max_score = len(scores) * 10
    final_score = (total_score / max_score) * 100
    answered_questions = len(scores)
    
    session_results_collection = db["session_results"]
    await session_results_collection.insert_one({
        "session_id": session_id,
        "user_id": user["user_id"],
        "final_score": round(final_score, 2),
        "total_questions": max_score // 10,
        "answered_questions": answered_questions,
        "accuracy": round((total_score / (answered_questions * 10)) * 100, 2),
        "status": "ended",
        "ended_at": datetime.now(timezone.utc)
    })

    session = await find_session_by_session_id(session_id, user["user_id"])
    if not session:
        return error_response(code=404, error_message="Session data not found")

    user_summary_collection = db["user_home_summary"]
    existing_summary = await user_summary_collection.find_one({"user_id": user["user_id"]})

    if existing_summary:
        new_total_interviews = existing_summary["total_interviews"] + 1
        new_total_answers = existing_summary["total_answers"] + len(scores)
        new_avg_score = ((existing_summary["avg_score"] * existing_summary["total_interviews"]) + final_score) / new_total_interviews
        new_accuracy = ((existing_summary["accuracy"] * existing_summary["total_answers"]) + sum(scores)) / new_total_answers

        await user_summary_collection.update_one(
            {"user_id": user["user_id"]},
            {
                "$set": {
                    "avg_score": round(new_avg_score, 2),
                    "accuracy": round(new_accuracy, 2),
                    "last_session": {
                        "session_id": session_id,
                        "job_title": session.get("job_title", "N/A"),
                        "final_score": round(final_score, 2),
                        "ended_at": datetime.now(timezone.utc)
                    },
                    "updated_at": datetime.now(timezone.utc)
                },
                "$inc": {
                    "total_interviews": 1,
                    "total_answers": len(scores)
                }
            }
        )
    else:
        await user_summary_collection.insert_one({
            "user_id": user["user_id"],
            "total_interviews": 1,
            "total_answers": len(scores),
            "avg_score": round(final_score, 2),
            "accuracy": round(sum(scores) / len(scores), 2),
            "last_session": {
                "session_id": session_id,
                "job_title": session.get("job_title", "N/A"),
                "final_score": round(final_score, 2),
                "ended_at": datetime.now(timezone.utc)
            },
            "updated_at":datetime.now(timezone.utc)
        })

    return success_response(code=200, data={
        "final_score": round(final_score, 2),
        "answered_questions": answered_questions,
        "message": "Session completed and evaluated successfully"
    })



@router.get("/api/sessions/{session_id}/score")
async def calculate_score(session_id: int, user=Depends(get_current_user)):
    is_valid = await validate_and_sync_session(session_id, user["user_id"])
    if not is_valid:
        return error_response(code=404, error_message="Session not found or unauthorized")

    answers = await get_all_answers_with_scores(session_id, user["user_id"])
    if not answers:
        return error_response(code=404, error_message="No answers with scores found for this session")

    scores = []
    question_scores = []

    for ans in answers:
        score = ans.get("similarity_score", 0)
        question_index = ans.get("question_index", -1)
        scores.append(score)
        question_scores.append({
            "question_index": question_index,
            "score": round(score, 2)
        })

    total_score = sum(scores)
    max_score = len(scores) * 10
    final_score = (total_score / max_score) * 100

    return success_response(code=200, data={
        "session_id": session_id,
        "answered_questions": len(scores),
        "final_score": round(final_score, 2),
        "question_scores": question_scores
    })

