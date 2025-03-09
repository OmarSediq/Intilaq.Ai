from fastapi import APIRouter, HTTPException ,UploadFile, File,Depends , Header
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel
from app.services.mongo_services import get_mongo_client
from app.services.redis_services import redis_client 
from app.services.ai_services import generate_interview_questions,analyze_interview_answer
from app.services.whisper_client import transcribe_audio

import json
import asyncio
import random
import tempfile

router = APIRouter()



async def get_db():
    client = await get_mongo_client()
    return client["interview_db"]


# model = whisper.load_model("small")  


class JobData(BaseModel):
    job_title: str
    level: str = None
    description: str = None


@router.post("/generate_questions/")
async def generate_questions(
    job_data: JobData,
    language: str = Header(default="en"),
    db=Depends(get_db)
):
    try:
        ai_questions = await generate_interview_questions(job_data.job_title, job_data.description, language)

        if not ai_questions:
            raise HTTPException(status_code=400, detail="No questions generated")

        questions_list = [q.strip() for q in ai_questions.split("\n") if q.strip()]

        session_id = random.randint(1000, 9999)

        await db["questions"].insert_one({
            "session_id": session_id,
            "job_title": job_data.job_title,
            "level": job_data.level,
            "language": language,
            "questions": questions_list,
            "current_question_index": 0
        })

        return {"session_id": session_id, "message": "Questions generated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating interview questions: {str(e)}")


@router.get("/stream_questions/{session_id}")
async def stream_questions(session_id: int, db=Depends(get_db)):
    session = await db["questions"].find_one({"session_id": session_id})

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = session["questions"]

    cleaned_questions = [q.strip() for q in questions if q.strip()]

    async def event_generator():
        for index, question in enumerate(cleaned_questions):
            yield f"data: {json.dumps({'question': question, 'index': index})}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")



@router.post("/submit_voice_answer/")
async def submit_voice_answer(
    session_id: str,  
    question_index: int,
    file: UploadFile = File(...),
    language: str = Header(default="en")
):
    try:
        text_answer = await transcribe_audio(file)  

        if not text_answer or "error" in text_answer:
            raise HTTPException(status_code=400, detail=f"Failed to transcribe audio: {text_answer.get('error', 'Unknown error')}")

        session = await redis_client.hgetall(f"session:{session_id}")
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        questions = session.get("questions", "").split("||")
        if question_index >= len(questions):
            raise HTTPException(status_code=400, detail="Invalid question index")

        correct_question = questions[question_index]

        ai_analysis = await analyze_interview_answer(text_answer, correct_question, language)

        await redis_client.hset(f"session:{session_id}:answers", question_index, text_answer)
        await redis_client.hset(f"session:{session_id}:feedbacks", question_index, ai_analysis["feedback"])
        await redis_client.hset(f"session:{session_id}:scores", question_index, ai_analysis["score"])

        return {
            "message": "Answer submitted successfully",
            "transcribed_text": text_answer,
            "feedback": ai_analysis["feedback"],
            "score": ai_analysis["score"],
            "model_answer": ai_analysis["model_answer"]
        }

    except HTTPException:
        raise  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing voice answer: {str(e)}")



@router.get("/stream_answers/{session_id}")
async def stream_answers(session_id: int):
    async def event_generator():
        while True:
            answers = await redis_client.hgetall(f"session:{session_id}:answers")  
            if answers:
                yield f"data: {json.dumps({'answers': answers})}\n\n"
            await asyncio.sleep(1)  

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/stream_feedback/{session_id}")
async def stream_feedback(session_id: int):    
    async def event_generator():
        while True:
            feedbacks = await redis_client.hgetall(f"session:{session_id}:feedbacks") 
            if feedbacks:
                yield f"data: {json.dumps({'feedbacks': feedbacks})}\n\n"
            await asyncio.sleep(1)  

    return StreamingResponse(event_generator(), media_type="text/event-stream")



@router.post("/start_session/")
async def start_session(session_id: int, db=Depends(get_db)):
    session = await db["questions"].find_one({"session_id": session_id}) 

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    redis_client.setex(f"session:{session_id}:status", 3600, "active")

    return {"message": "Session started"}



@router.post("/end_session/")
async def end_session(session_id: int):

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
