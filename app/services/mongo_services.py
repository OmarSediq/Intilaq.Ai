from bson import ObjectId
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio
import time

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

mongo_client = None
mongo_db = None
mongo_ready = asyncio.Event()  #

async def connect_to_mongo():
    global mongo_client, mongo_db
    retries = 5
    while retries > 0:
        try:
            mongo_client = AsyncIOMotorClient(MONGO_URI, maxPoolSize=10, minPoolSize=5)
            mongo_db = mongo_client[MONGO_DB_NAME]
            print("MongoDB Connected!")
            return
        except Exception as e:
            print(f"MongoDB not ready, retrying... ({retries} attempts left)")
            time.sleep(5)
            retries -= 1
    raise Exception("Failed to connect to MongoDB after multiple attempts.")

async def close_mongo_connection():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.")

async def get_mongo_client():
    await mongo_ready.wait()  
    return mongo_client
