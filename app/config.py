from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB Configuration
    MONGO_URI: str
    MONGO_DB_NAME: str
    
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
    

    # Redis Expiry Settings
    REDIS_OTP_EXPIRE_SECONDS: int = 300
    REDIS_2FA_EXPIRE_SECONDS: int = 300
    GENAI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
