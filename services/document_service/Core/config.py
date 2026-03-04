from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
class Settings(BaseSettings):
    # ---- Redis ----
    REDIS_URL: str
    REDIS_STREAM_DOCUMENT: str
    REDIS_CONSUMER_GROUP_DOCUMENT: str
    SERVICE_NAME: str 

    MONGO_URI: str
    MONGO_DB_NAME: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str

    class Config:
        env_file = ".env"
settings = Settings()
