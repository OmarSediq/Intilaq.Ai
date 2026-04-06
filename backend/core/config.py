from pydantic_settings import BaseSettings

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
