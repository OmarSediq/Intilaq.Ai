from bson import ObjectId
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio
from fastapi import  HTTPException 
 
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

mongo_client = None
mongo_db = None
mongo_ready = asyncio.Event() 


async def get_db():
    client = await get_mongo_client()
    if client is None: 
        raise HTTPException(status_code=500, detail="MongoDB connection is not available")
    return client["interview_db"]

async def connect_to_mongo():
    global mongo_client, mongo_db
    retries = 5
    while retries > 0:
        try:
            mongo_client = AsyncIOMotorClient(MONGO_URI, maxPoolSize=10, minPoolSize=5)
            mongo_db = mongo_client[MONGO_DB_NAME]
            print("MongoDB Connected!")
            mongo_ready.set()  
            return
        except Exception as e:
            print(f"MongoDB not ready, retrying... ({retries} attempts left)")
            await asyncio.sleep(5)
            retries -= 1
    raise Exception("Failed to connect to MongoDB after multiple attempts.")


async def close_mongo_connection():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.")


async def get_mongo_client():
    await mongo_ready.wait()  
    if mongo_client is None:  
        raise Exception("MongoDB client is not initialized properly")
    return mongo_client



async def insert_question_session(session_data: dict):
    db = await get_db()
    return await db["questions"].insert_one(session_data)

async def find_session_by_user_id(user_id: str):
    db = await get_db()
    return await db["questions"].find_one({"user_id": user_id})

async def find_session_by_session_id(session_id: int, user_id: str):
    if not user_id:
        raise HTTPException(status_code=403, detail="User not authorized")

    db = await get_db()
    query = {"session_id": session_id, "user_id": user_id}
    session = await db["questions"].find_one(query)

    if not session:
        print(f"[❌ Session Not Found] user_id={user_id} session_id={session_id}")
        raise HTTPException(status_code=404, detail="Session not found or unauthorized")

    return session


async def insert_user_answer(answer_data: dict):
    db = await get_db()
    return await db["answers"].insert_one(answer_data)

async def find_latest_answer(session_id: int, user_id: str):
    db = await get_db()
    return await db["answers"].find_one(
        {"session_id": session_id, "user_id": user_id},
        sort=[("question_index", -1)]
    )

async def update_answer_feedback(session_id: int, user_id: str, question_index: int, feedback_data: dict):
    db = await get_db()
    return await db["answers"].update_one(
        {"session_id": session_id, "user_id": user_id, "question_index": question_index},
        {"$set": feedback_data}
    )

async def get_all_answers_with_scores(session_id: int, user_id: str):
    db = await get_db()
    return await db["answers"].find(
        {"session_id": session_id, "user_id": user_id},
        {"similarity_score": 1, "question_index": 1}
    ).to_list(length=None)
