from fastapi import APIRouter, HTTPException ,UploadFile, File,Depends 
from pydantic import BaseModel
from app.services.mongo_services import get_mongo_client
from app.services.redis_services import redis_client 
from app.services.ai_services import generate_interview_questions,generate_best_model_answer,generate_feedback , analyze_answer
from app.routers.auth import get_current_user
import asyncio
import random
import os 
import httpx
# from app.services.whisper_service import model  
from datetime import datetime
router = APIRouter()

WHISPER_SERVICE_URL = os.getenv("WHISPER_SERVICE_URL", "http://whisper-container:5001/transcribe")
async def get_db():
    client = await get_mongo_client()
    if client is None: 
        raise HTTPException(status_code=500, detail="MongoDB connection is not available")
    return client["interview_db"]


# async def get_db():
#     client = await get_mongo_client()  
#     return client["interview_db"]

# model = whisper.load_model("small")  
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

@router.get("/job_titles", tags=["Reference Data"])
async def get_job_titles(db=Depends(get_db)):
    try:
        job_titles_collection = db["job_titles"]
        titles = await job_titles_collection.distinct("title")  

        return {"job_titles": titles}  

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job titles: {str(e)}")

@router.get("/job_levels", tags=["Reference Data"])
async def get_job_levels(db=Depends(get_db)):
    try:
        job_levels_collection = db["job_levels"]
        levels = await job_levels_collection.distinct("level")  

        return {"job_levels": levels}  

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job levels: {str(e)}")
    
  
@router.post("/generate_questions/")
async def generate_questions(
    job_data: JobData,
    db=Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        ai_questions = await generate_interview_questions(job_data.job_title, job_data.level, job_data.description)

        if not ai_questions:
            raise HTTPException(status_code=400, detail="No questions generated")

        questions_list = [q.strip() for q in ai_questions.split("\n") if q.strip()]

        session_id = random.randint(1000, 9999)

        best_model_answers = await asyncio.gather(
            *[generate_best_model_answer(q) for q in questions_list]
        )

  
        questions_with_answers = [
            {"question_index": idx, "question": q, "best_model_answer": a}
            for idx, (q, a) in enumerate(zip(questions_list, best_model_answers))
        ]

        await db["questions"].insert_one({
            "session_id": session_id,
            "user_id": user["user_id"],
            "job_title": job_data.job_title,
            "level": job_data.level,
            "questions": questions_with_answers,
            "current_question_index": 0 
        })

        async with redis_client.pipeline() as pipe:
            pipe.set(f"user:{user['user_id']}:session", int(session_id))
            pipe.set(f"session:{session_id}:current_question", 0)
            await pipe.execute()

        return {"message": "Questions generated successfully", "session_id": session_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating interview questions: {str(e)}")

    

@router.get("/get_questions/")
async def get_questions(user_session=Depends(get_interview_session_data), db=Depends(get_db)):

    session_id = int(user_session["session_id"]) 

    session = await db["questions"].find_one(
        {"session_id": session_id},  
        {"questions.question": 1, "_id": 0}
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    questions_only = [q["question"] for q in session["questions"]]  
    return {
        "session_id": session_id,
        "questions": questions_only
    }





@router.post("/start_session/")
async def start_session(db=Depends(get_db), user=Depends(get_current_user)):
        
    session_id = await redis_client.get(f"user:{user['user_id']}:session")
    if not session_id:
        raise HTTPException(status_code=404, detail="No active session found")

    session_id = int(session_id)  
    session = await db["questions"].find_one({"session_id": session_id})

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    async with redis_client.pipeline() as pipe:
        pipe.set(f"session:{session_id}:status", "active")  # 
        pipe.set(f"session:{session_id}:current_question", 0)  
        await pipe.execute()

    return {"message": "Session started successfully", "session_id": session_id}



@router.get("/get_next_question/")
async def get_next_question(user_session=Depends(get_interview_session_data), db=Depends(get_db)):
    session_id = int(user_session["session_id"])
    current_index = user_session["current_question_index"]

    session = await db["questions"].find_one({"session_id": session_id}, {"questions": 1})
    if not session or "questions" not in session:
        raise HTTPException(status_code=404, detail="Session not found or no questions available.")

    questions = session["questions"]
    total_questions = len(questions)

    if current_index >= total_questions:
        return {"message": "No more questions available."}

    question = questions[current_index]

    async with redis_client.pipeline() as pipe:
        pipe.set(f"session:{session_id}:current_question", current_index + 1)
        await pipe.execute()

    return {
        "question": question["question"],
        "question_index": current_index
    }



@router.post("/submit_answer/")
async def submit_answer(
    user_session=Depends(get_interview_session_data),  
    file: UploadFile = File(...),
    db=Depends(get_db)
):
    session_id = int(user_session["session_id"])
    current_question_index = user_session["current_question_index"]

    session = await db["questions"].find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if current_question_index >= len(session["questions"]):
        raise HTTPException(status_code=400, detail="No more questions remaining")

    try:
        print(f"📂 DEBUG: File received - Name: {file.filename}, Type: {file.content_type}")

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            files = {"file": (file.filename, file.file.read(), file.content_type)}
            response = await client.post(WHISPER_SERVICE_URL, files=files)

        print(f"🛠️ DEBUG: Whisper API Response - Status {response.status_code}, Content: {response.text}")

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Whisper API error: {response.text}")

        result = response.json()
        transcribed_text = result.get("text", "").strip()

        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Transcription failed, no text found.")

        answer_record = {
            "session_id": session_id,
            "user_id": user_session["user_id"],
            "question_index": current_question_index,
            "answer_text": transcribed_text,
            "timestamp": datetime.utcnow()
        }

        insert_result = await db["answers"].insert_one(answer_record)

        if not insert_result.inserted_id:
            raise Exception("Failed to save answer in MongoDB.")

        async with redis_client.pipeline() as pipe:
            pipe.sadd(f"session:{session_id}:completed_questions", current_question_index)
            await pipe.execute()

        return {
            "message": "Answer submitted successfully",
            "question_index": current_question_index,
            "transcribed_text": transcribed_text
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: {error_details}")
        raise HTTPException(status_code=500, detail=f"Speech-to-Text failed: {str(e)}")

    
@router.get("/get_feedback/")
async def get_feedback(user_session=Depends(get_interview_session_data), db=Depends(get_db)):
    session_id = int(user_session["session_id"])

    latest_answer = await db["answers"].find_one(
        {"session_id": session_id, "user_id": user_session["user_id"]},
        sort=[("question_index", -1)]  
    )

    if not latest_answer:
        raise HTTPException(status_code=404, detail="User answer not found")

    question_index = latest_answer["question_index"]
    
    session = await db["questions"].find_one(
        {"session_id": session_id, "questions": {"$elemMatch": {"question_index": question_index}}},  
        {"questions.$": 1} 
    )

    if not session or "questions" not in session or not session["questions"]:
        raise HTTPException(status_code=400, detail="Question not found in session")

    question_data = session["questions"][0]  
    question_text = question_data["question"]
    ideal_answer = question_data.get("best_model_answer", "N/A")  

    user_answer_text = latest_answer["answer_text"]
    feedback = generate_feedback(user_answer_text)

    return {
        "question": question_text,  
        "user_answer": user_answer_text,
        "ideal_answer": ideal_answer,  
        **feedback  
    }



@router.post("/end_session/")
async def end_session(user_session=Depends(get_interview_session_data)):
    session_id = int(user_session["session_id"]) 

    scores = await redis_client.hgetall(f"session:{session_id}:scores")  

    if not scores:
        raise HTTPException(status_code=404, detail="No scores found for this session")

    total_score = sum(map(int, scores.values()))
    max_possible_score = len(scores) * 100  
    final_score = (total_score / max_possible_score) * 100

    await redis_client.delete(f"session:{session_id}:answers")  
    await redis_client.delete(f"session:{session_id}:feedbacks")  
    await redis_client.delete(f"session:{session_id}:scores")  

    return {"final_score": round(final_score, 2), "message": "Session completed"}



@router.get("/analyze_answer/")
async def analyze_user_answer(
    user_session=Depends(get_interview_session_data),
    db=Depends(get_db)
):
    session_id = int(user_session["session_id"])

    latest_answer = await db["answers"].find_one(
        {"session_id": session_id, "user_id": user_session["user_id"]},
        sort=[("question_index", -1)]
    )

    if not latest_answer:
        raise HTTPException(status_code=404, detail="User answer not found")

    question_index = latest_answer["question_index"]

    session = await db["questions"].find_one(
        {"session_id": session_id, "questions": {"$elemMatch": {"question_index": question_index}}},
        {"questions.$": 1}  
    )

    if not session or "questions" not in session or not session["questions"]:
        raise HTTPException(status_code=400, detail="Question not found in session")

    question_data = session["questions"][0]  
    question_text = question_data["question"]
    ideal_answer = question_data.get("best_model_answer", "N/A")

    user_answer_text = latest_answer["answer_text"]

    score = analyze_answer(user_answer_text, ideal_answer)

    return {
        "question": question_text,
        "user_answer": user_answer_text,
        "ideal_answer": ideal_answer,
        "similarity_score": score,
        "message": "The similarity score ranges from 0 to 10. A higher score means the answer is closer to the ideal answer."
    }


