from pydantic_settings import BaseSettings
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = "/app/templates"
# PDF_DIR = "/app/generated_pdfs" 

print(f"Templates directory: {TEMPLATES_DIR}")
# print(f"PDF directory: {PDF_DIR}")

if not os.path.exists(TEMPLATES_DIR):
    print(f"Warning: Templates directory '{TEMPLATES_DIR}' does not exist!")

if not os.path.exists(os.path.join(TEMPLATES_DIR, "resume_template.html")):
    print("Warning: Template 'resume_template.html' not found in:", TEMPLATES_DIR)

# os.makedirs(PDF_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def date_format(value):
    if value:
        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime("%b %Y") 
        except ValueError:
            return value  
    return "Present"  

env.filters['date_format'] = date_format
class Settings(BaseSettings):
    # MongoDB Configuration
    MONGO_URI: str
    MONGO_DB_NAME: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    # Redis Configuration
    REDIS_URL: str
    
    # PostgreSQL Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_URL: str

    # SMTP (Email) Configurations
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str

    # Security Configurations
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Whisper Microservice
    WHISPER_SERVICE_URL: str
    whisper_model_path: str = "/whisper_model"
    whisper_model_name: str = "base.en"


    # Redis Expiry Settings
    REDIS_OTP_EXPIRE_SECONDS: int = 300
    REDIS_2FA_EXPIRE_SECONDS: int = 300
    GENAI_API_KEY: str
    enable_remote_debug: bool = False
    # mentoring settings
    enable_tracing: bool = False
    jaeger_endpoint: str = "http://localhost:4317"
    service_name: str = "my-service"

      # -- REDIS STREAMS (from your .env)
    redis_stream_video: str = "intilaq:job:video"
    redis_stream_text: str = "intilaq:job:text"
    redis_stream_notification: str = "intilaq:event:notification"
    redis_stream_document: str = "intilaq:event:document"
    REDIS_CONSUMER_GROUP_NOTIFICATION: str

    REDIS_CONSUMER_GROUP_DOCUMENT:str

    # # -- CONSUMER GROUP NAMES
    # redis_consumer_group_video: str = "intilaq:cp:video"
    # redis_consumer_group_text: str = "intilaq:cp:text"
    # # redis_consumer_group_email: str = "intilaq:cp:email"
    # redis_consumer_group_docs: str = "intilaq:cp:docs"

    # -- IDEMPOTENCY & CLAIMS SETTINGS
    idempotency_use_redis: bool = True
    idempotency_claim_ttl_seconds: int = 60
    job_cache_ttl_seconds: int = 3600

    # -- TASK RETENTION SETTINGS
    task_max_attempts: int = 5
    task_retention_days: int = 90
    class Config:
        env_file = ".env"

settings = Settings()
