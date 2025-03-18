from fastapi import APIRouter, HTTPException ,UploadFile, File,Depends 
from pydantic import BaseModel
from app.services.mongo_services import get_mongo_client
from app.services.redis_services import redis_client 
from app.services.ai_services import generate_interview_questions,generate_best_model_answer
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
    # 🔹 جلب `session_id` من Redis
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

    current_question_index = int(results[0]) if results[0] else 0
    completed_questions = list(map(int, results[1])) if results[1] else []

    print(f"🔍 DEBUG: session_id={session_id}, type={type(session_id)}, current_question_index={current_question_index}")

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
            {"question": q, "best_model_answer": a} for q, a in zip(questions_list, best_model_answers)
        ]

        session_id = random.randint(1000, 9999)  

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

    if user_session["session_status"] == "completed":
        return {"message": "Session is already completed"}

    session = await db["questions"].find_one({"session_id": user_session["session_id"]})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    current_index = user_session["current_question_index"]
    if current_index >= len(session["questions"]):
        return {"message": "No more questions"}

    question = session["questions"][current_index]

    async with redis_client.pipeline() as pipe:
        pipe.set(f"session:{user_session['session_id']}:current_question", current_index + 1)
        await pipe.execute()

    return {"question": question, "question_index": current_index}


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

        await db["answers"].insert_one({
            "session_id": session_id,
            "user_id": user_session["user_id"],
            "question_index": current_question_index,
            "answer_text": transcribed_text,
            "timestamp": datetime.utcnow()
        })

        async with redis_client.pipeline() as pipe:
            pipe.sadd(f"session:{session_id}:completed_questions", current_question_index)
            next_question_index = current_question_index + 1
            if next_question_index < len(session["questions"]):
                pipe.set(f"session:{session_id}:current_question", next_question_index)
            else:
                pipe.set(f"session:{session_id}:status", "completed")  
            await pipe.execute()

        return {
            "message": "Answer submitted successfully",
            "question_index": current_question_index,
            "transcribed_text": transcribed_text,
            "next_question_index": next_question_index if next_question_index < len(session["questions"]) else None
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: {error_details}")
        raise HTTPException(status_code=500, detail=f"Speech-to-Text failed: {str(e)}")



# @router.get("/stream_answers/{session_id}")
# async def stream_answers(session_id: int):
#     async def event_generator():
#         while True:
#             answers = await redis_client.hgetall(f"session:{session_id}:answers")  
#             if answers:
#                 yield f"data: {json.dumps({'answers': answers})}\n\n"
#             await asyncio.sleep(1)  

#     return StreamingResponse(event_generator(), media_type="text/event-stream")




# @router.post("/submit_voice_answer/")
# async def submit_voice_answer(
#     session_id: str,  
#     question_index: int,
#     file: UploadFile = File(...),
#     language: str = Header(default="en")
# ):
#     try:
#         text_answer = await transcribe_audio(file)  

#         if not text_answer or "error" in text_answer:
#             raise HTTPException(status_code=400, detail=f"Failed to transcribe audio: {text_answer.get('error', 'Unknown error')}")

#         session = await redis_client.hgetall(f"session:{session_id}")
#         if not session:
#             raise HTTPException(status_code=404, detail="Session not found")

#         questions = session.get("questions", "").split("||")
#         if question_index >= len(questions):
#             raise HTTPException(status_code=400, detail="Invalid question index")

#         correct_question = questions[question_index]

#         ai_analysis = await analyze_interview_answer(text_answer, correct_question, language)

#         await redis_client.hset(f"session:{session_id}:answers", question_index, text_answer)
#         await redis_client.hset(f"session:{session_id}:feedbacks", question_index, ai_analysis["feedback"])
#         await redis_client.hset(f"session:{session_id}:scores", question_index, ai_analysis["score"])

#         return {
#             "message": "Answer submitted successfully",
#             "transcribed_text": text_answer,
#             "feedback": ai_analysis["feedback"],
#             "score": ai_analysis["score"],
#             "model_answer": ai_analysis["model_answer"]
#         }

#     except HTTPException:
#         raise  
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing voice answer: {str(e)}")




# @router.get("/stream_feedback/{session_id}")
# async def stream_feedback(session_id: int):    
#     async def event_generator():
#         while True:
#             feedbacks = await redis_client.hgetall(f"session:{session_id}:feedbacks") 
#             if feedbacks:
#                 yield f"data: {json.dumps({'feedbacks': feedbacks})}\n\n"
#             await asyncio.sleep(1)  

#     return StreamingResponse(event_generator(), media_type="text/event-stream")


# @router.post("/start_session/")
# async def start_session(
#     session_id: int,
#     request: Request,
#     response: Response,
#     db=Depends(get_db),  # MongoDB
#     pg_db=Depends(get_db_pg),  # PostgreSQL
#     user=Depends(get_current_user)  # استخراج `user_id` من `JWT Token`
# ):
#     session = await db["questions"].find_one({"session_id": session_id})
#     if not session:
#         raise HTTPException(status_code=404, detail="Session not found in MongoDB")

#     existing_session = await pg_db.fetchrow("SELECT * FROM sessions WHERE session_id = $1", session_id)
#     if existing_session:
#         raise HTTPException(status_code=400, detail="Session already exists in PostgreSQL")

#     query = "INSERT INTO sessions (session_id, user_id, status) VALUES ($1, $2, 'active')"
#     await pg_db.execute(query, session_id, user["id"])

#     await redis_client.setex(f"session:{session_id}:status", 1800, "active")  # الجلسة تبقى نشطة لمدة ساعة

#     return {"message": "Session started successfully", "session_id": session_id}


# @router.websocket("/ws/")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
    
#     try:
#         user = await get_current_user(websocket=websocket)
#         print(f"User Authenticated: {user}")

#         await websocket.send_text(f"Welcome, {user['id']}!")

#     except HTTPException as e:
#         await websocket.close(code=4001)
#         return


# @router.post("/end_session/")
# async def end_session(session_id: int):

#     scores = await redis_client.hgetall(f"session:{session_id}:scores")  

#     if not scores:
#         raise HTTPException(status_code=404, detail="No scores found for this session")

#     total_score = sum(map(int, scores.values()))
#     max_possible_score = len(scores) * 100  
#     final_score = (total_score / max_possible_score) * 100

#     await redis_client.delete(f"session:{session_id}:answers")  
#     await redis_client.delete(f"session:{session_id}:feedbacks")  
#     await redis_client.delete(f"session:{session_id}:scores") 

#     return {"final_score": round(final_score, 2), "message": "Session completed"}
