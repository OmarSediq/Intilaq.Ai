from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from passlib.context import CryptContext
import os 
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


# -------------------- PostgreSQL Configuration -------------------- #

# Initialize the asynchronous PostgreSQL engine
postgres_engine = create_async_engine(settings.POSTGRES_URL, future=True, echo=True)

# Create a sessionmaker for PostgreSQL
SessionLocal = sessionmaker(bind=postgres_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db(request: Request) -> AsyncSession:
    async with SessionLocal() as session:
        request.state.db = session  # مهم للـ Middleware
        yield session

# -------------------- Password Hashing Configuration -------------------- #

# Initialize password hashing using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Generates a hashed password using bcrypt.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

# -------------------- MongoDB Configuration -------------------- #

try:
    # Initialize the MongoDB client
    mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
    mongo_db = mongo_client[settings.MONGO_DB_NAME]
    print("MongoDB connection successful.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# -------------------- Redis Configuration -------------------- #

async def get_redis_client():
    """
    Provides a Redis client instance with error handling.
    """
    try:
        client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
        await client.ping()
        print("Redis connection successful.")
        return client
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        return None

def get_collection(collection_name: str):
    """
    Get a collection from the MongoDB database.

    Args:
        collection_name (str): The name of the collection.

    Returns:
        Collection: The MongoDB collection.
    """
    return mongo_db[collection_name]



