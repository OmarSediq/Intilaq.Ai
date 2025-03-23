from fastapi import APIRouter, HTTPException ,UploadFile, File,Depends 
from pydantic import BaseModel
from app.services.mongo_services import get_mongo_client,insert_question_session,find_session_by_session_id ,insert_user_answer,update_answer_feedback,find_latest_answer,get_all_answers_with_scores 
from app.services.redis_services import redis_client ,set_user_session_id, set_current_question_index,get_current_question_index,add_completed_question,set_session_status
from app.services.ai_services import generate_interview_questions,generate_best_model_answer,generate_feedback , analyze_answer
from app.routers.auth import get_current_user
import asyncio
import random
import os 
import httpx
from datetime import datetime
router = APIRouter()
       

WHISPER_SERVICE_URL = os.getenv("WHISPER_SERVICE_URL", "http://whisper-container:5001/transcribe")

async def get_db():
    client = await get_mongo_client()
    if client is None: 
        raise HTTPException(status_code=500, detail="MongoDB connection is not available")
    return client["interview_db"]


async def get_interview_session_data(user=Depends(get_current_user), db=Depends(get_db)):
    session_id = await redis_client.get(f"user:{user['user_id']}:session")

    if session_id:
        session_id = int(session_id)  
    else:
        session = await db["questions"].find_one({"user_id": user["user_id"]})
        if session:
            session_id = int(session["session_id"])  
            await redis_client.set(f"user:{user['user_id']}:session", session_id)  
        else:
            raise HTTPException(status_code=404, detail="No active session found")

    async with redis_client.pipeline() as pipe:
        pipe.get(f"session:{session_id}:current_question")
        pipe.smembers(f"session:{session_id}:completed_questions")
        results = await pipe.execute()

    if results[0] is None:
        session = await db["questions"].find_one({"session_id": session_id}, {"current_question_index": 1})
        current_question_index = session["current_question_index"] if session else 0
        await redis_client.set(f"session:{session_id}:current_question", current_question_index)
    else:
        current_question_index = int(results[0])

    completed_questions = list(map(int, results[1])) if results[1] else []

    print(f"🔍 DEBUG: session_id={session_id}, current_question_index={current_question_index}")

    return {
        "session_id": session_id,  
        "user_id": user["user_id"],
        "current_question_index": current_question_index,
        "completed_questions": completed_questions
    }



class JobData(BaseModel):
    job_title: str
    level: str = None
    description: str = None

@router.get("/api/sessions/job-titles", tags=["Reference Data"])
async def get_job_titles(db=Depends(get_db)):
    try:
        job_titles_collection = db["job_titles"]
        titles = await job_titles_collection.distinct("title")  

        return {"job_titles": titles}  

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job titles: {str(e)}")

@router.get("/api/sessions/job-levels", tags=["Reference Data"])
async def get_job_levels(db=Depends(get_db)):
    try:
        job_levels_collection = db["job_levels"]
        levels = await job_levels_collection.distinct("level")  

        return {"job_levels": levels}  

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job levels: {str(e)}")



@router.post("/api/sessions/", tags=["Interview Sessions"])
async def create_interview_session(
    job_data: JobData,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        # 1. Generate AI questions
        ai_questions = await generate_interview_questions(job_data.job_title, job_data.level, job_data.description)
        if not ai_questions:
            raise HTTPException(status_code=400, detail="No questions generated")

        questions_list = [q.strip() for q in ai_questions.split("\n") if q.strip()]

        # 2. Generate session ID
        session_id = random.randint(100000, 999999)

        # 3. Generate model answers
        best_model_answers = await asyncio.gather(
            *[generate_best_model_answer(q) for q in questions_list]
        )

        # 4. Format questions and answers
        questions_with_answers = [
            {"question_index": idx, "question": q, "best_model_answer": a}
            for idx, (q, a) in enumerate(zip(questions_list, best_model_answers))
        ]

        # 5. Store session in Mongo
        session_data = {
            "session_id": session_id,
            "user_id": user["user_id"],
            "job_title": job_data.job_title,
            "level": job_data.level,
            "questions": questions_with_answers,
            "current_question_index": 0
        }
        await insert_question_session(session_data)

        # 6. Store session info in Redis
        await set_user_session_id(user["user_id"], session_id)
        await set_current_question_index(session_id, 0)

        return {"message": "Interview session created", "session_id": session_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating interview session: {str(e)}")


    


@router.get("/api/sessions/{session_id}/questions")
async def get_questions(session_id: int, user=Depends(get_current_user)):
    session = await find_session_by_session_id(session_id, user["user_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    questions_only = [q["question"] for q in session["questions"]]
    return {"session_id": session_id, "questions": questions_only}




@router.get("/api/sessions/{session_id}/questions/next")
async def get_next_question(session_id: int, user=Depends(get_current_user)):
    session = await find_session_by_session_id(session_id, user["user_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    current_index = await get_current_question_index(session_id)
    questions = session["questions"]

    if current_index >= len(questions):
        return {"message": "No more questions available."}

    question = questions[current_index]
    await set_current_question_index(session_id, current_index + 1)

    return {
        "question": question["question"],
        "question_index": current_index
    }



@router.post("/api/sessions/{session_id}/answers")
async def submit_answer(session_id: int, file: UploadFile = File(...), user=Depends(get_current_user)):
    session = await find_session_by_session_id(session_id, user["user_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    current_index = await get_current_question_index(session_id)
    if current_index >= len(session["questions"]):
        raise HTTPException(status_code=400, detail="No more questions remaining")

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            files = {"file": (file.filename, file.file.read(), file.content_type)}
            response = await client.post(WHISPER_SERVICE_URL, files=files)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Whisper API error: {response.text}")

        transcribed_text = response.json().get("text", "").strip()
        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Transcription failed, no text found.")

        await insert_user_answer({
            "session_id": session_id,
            "user_id": user["user_id"],
            "question_index": current_index,
            "answer_text": transcribed_text,
            "timestamp": datetime.utcnow()
        })

        await add_completed_question(session_id, current_index)

        return {
            "message": "Answer submitted successfully",
            "question_index": current_index,
            "transcribed_text": transcribed_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech-to-Text failed: {str(e)}")


@router.get("/api/sessions/{session_id}/answers/{question_index}/feedback")
async def get_feedback(session_id: int, question_index: int, user=Depends(get_current_user)):
    latest_answer = await find_latest_answer(session_id, user["user_id"])
    if not latest_answer:
        raise HTTPException(status_code=404, detail="User answer not found")

    session = await find_session_by_session_id(session_id, user["user_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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

    return {
        "question": question_text,
        "user_answer": user_answer,
        "ideal_answer": ideal_answer,
        **feedback,
        "similarity_score": similarity_score
    }

@router.post("/api/sessions/{session_id}/start")
async def start_session(session_id: int, user=Depends(get_current_user)):
    session = await find_session_by_session_id(session_id, user["user_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await set_session_status(session_id, "active")
    await set_current_question_index(session_id, 0)

    return {"message": "Session started successfully", "session_id": session_id}


@router.post("/api/sessions/{session_id}/end")
async def end_session(session_id: int, user=Depends(get_current_user)):
    answers = await get_all_answers_with_scores(session_id, user["user_id"])
    if not answers:
        raise HTTPException(status_code=404, detail="No answers with scores found for this session")

    scores = [ans.get("similarity_score", 0) for ans in answers]
    if not scores:
        raise HTTPException(status_code=404, detail="No similarity scores found")

    total_score = sum(scores)
    max_score = len(scores) * 10
    final_score = (total_score / max_score) * 100

    await set_session_status(session_id, "ended")

    return {
        "final_score": round(final_score, 2),
        "answered_questions": len(scores),
        "message": "Session completed and evaluated successfully"
    }

@router.get("/api/sessions/{session_id}/score")
async def calculate_score(session_id: int, user=Depends(get_current_user)):
    answers = await get_all_answers_with_scores(session_id, user["user_id"])
    if not answers:
        raise HTTPException(status_code=404, detail="No answers with scores found for this session")

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

    return {
        "session_id": session_id,
        "answered_questions": len(scores),
        "final_score": round(final_score, 2),
        "question_scores": question_scores
    }
