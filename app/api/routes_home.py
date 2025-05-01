# tailscale funnel --https=8443 http://localhost:8443
# tailscale serve --https=8443 http://localhost:8443
# tailscale serve status
#openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
from fastapi import APIRouter, Depends
from app.services.mongo_services import get_db
from app.api.routes_auth import get_current_user
from app.utils.response_schemas import success_response, error_response
from app.services.redis_services import get_user_session_ids
from datetime import datetime
from app.api.routes_interview import validate_and_sync_session
from app.services.mongo_services import get_mongo_client
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from fastapi.responses import StreamingResponse
from io import BytesIO


router = APIRouter()

@router.get("/api/home/summary", tags=["Home Summary"])
async def get_home_summary(user=Depends(get_current_user), db=Depends(get_db)):
    try:
        summary_collection = db["user_home_summary"]

        user_summary = await summary_collection.find_one(
            {"user_id": user["user_id"]},
            {"_id": 0, "total_interviews": 1, "total_answers": 1, "avg_score": 1, "accuracy": 1}
        )

        if not user_summary:
            return success_response(code=200, data={
                "total_interviews": 0,
                "total_answers": 0,
                "avg_score": 0.0,
                "accuracy": 0.0
            })

        return success_response(code=200, data=user_summary)

    except Exception as e:
        return error_response(code=500, error_message=f"Failed to fetch home summary: {str(e)}")
    

def format_datetime(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()  
    return None

@router.get("/api/home/interview-sessions", tags=["Home Summary"])
async def get_user_interview_sessions(user=Depends(get_current_user), db=Depends(get_db)):
    try:
        session_ids = await get_user_session_ids(user["user_id"])

        if not session_ids:
            return success_response(code=200, data={"sessions": []})

        sessions_data = []

        for session_id in session_ids:
            session_doc = await db["questions"].find_one(
                {"session_id": session_id, "user_id": user["user_id"]},
                {"_id": 0, "job_title": 1, "level": 1, "created_at": 1, "questions": 1}
            )

            if not session_doc or not session_doc.get("questions"):
                continue

            first_question = session_doc["questions"][0].get("question") if session_doc["questions"] else None

            answer_doc = await db["answers"].find_one(
                {"session_id": session_id, "user_id": user["user_id"], "question_index": 0},
                {"_id": 0, "answer_text": 1, "feedback": 1}
            )

            session_info = {
                "session_id": session_id,
                "job_title": session_doc.get("job_title", "Unknown"),
                "level": session_doc.get("level", "Unknown"),
                "created_at": format_datetime(session_doc.get("created_at")),
                "question": first_question,
                "answer_text": answer_doc.get("answer_text") if answer_doc else None,
                "feedback": answer_doc.get("feedback") if answer_doc else None,
            }

            sessions_data.append(session_info)

        return success_response(code=200, data={"sessions": sessions_data})

    except Exception as e:
        return error_response(code=500, error_message=f"Failed to fetch user sessions: {str(e)}")


@router.get("/api/sessions/{session_id}/details", tags=["Interview Sessions"])
async def get_session_full_details(session_id: int, user=Depends(get_current_user), db=Depends(get_db)):
    try:
        is_valid = await validate_and_sync_session(session_id, user["user_id"])
        if not is_valid:
            return error_response(code=404, error_message="Session not found or unauthorized")
        
        session_doc = await db["questions"].find_one(
            {"session_id": session_id, "user_id": user["user_id"]},
            {"_id": 0, "questions": 1, "job_title": 1, "level": 1, "created_at": 1}
        )
        
        if not session_doc:
            return error_response(code=404, error_message="Session not found")

        answers_cursor = db["answers"].find(
            {"session_id": session_id, "user_id": user["user_id"]},
            {"_id": 0, "question_index": 1, "answer_text": 1, "feedback": 1}
        )
        answers_list = await answers_cursor.to_list(length=None)

        answers_map = {a["question_index"]: a for a in answers_list}

        session_questions = []
        for q in session_doc.get("questions", []):
            question_index = q.get("question_index")
            question_text = q.get("question")
            best_model_answer = q.get("best_model_answer")
            user_answer = answers_map.get(question_index, {}).get("answer_text")
            feedback = answers_map.get(question_index, {}).get("feedback")

            session_questions.append({
                "question_index": question_index,
                "question": question_text,
                "best_model_answer": best_model_answer,
                "user_answer": user_answer,
                "feedback": feedback
            })

        session_result = await db["session_results"].find_one(
            {"session_id": session_id, "user_id": user["user_id"]},
            {"_id": 0, "final_score": 1}
        )

        return success_response(code=200, data={
            "session_id": session_id,
            "job_title": session_doc.get("job_title", "Unknown"),
            "level": session_doc.get("level", "Unknown"),
            "created_at": session_doc.get("created_at").isoformat() if session_doc.get("created_at") else None,
            "questions": session_questions,
            "final_score": session_result.get("final_score") if session_result else None
        })

    except Exception as e:
        return error_response(code=500, error_message=f"Failed to fetch session details: {str(e)}")



@router.get("/api/resumes/download", tags=["My Resume"])
async def download_latest_resume_for_user(
    user=Depends(get_current_user),
    db=Depends(get_mongo_client)
):
    try:
        mongo_db = db["resumes_db"]

        file_doc = await mongo_db["fs.files"].find_one(
            {"metadata.user_id": int(user["user_id"])},
            sort=[("uploadDate", -1)] 
        )

        if not file_doc:
            return error_response(code=404, error_message="No resume found for this user")

        fs = AsyncIOMotorGridFSBucket(mongo_db)
        stream = await fs.open_download_stream(file_doc["_id"])
        content = await stream.read()

        return StreamingResponse(
            BytesIO(content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={file_doc.get('filename', 'resume')}.pdf"}
        )

    except Exception as e:
        return error_response(code=500, error_message=f"Error fetching resume: {str(e)}")
