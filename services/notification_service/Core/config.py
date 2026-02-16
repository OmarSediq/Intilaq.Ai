from pydantic_settings import BaseSettings
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

TEMPLATES_DIR = "/app/templates"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def date_format(value):
    if value:
        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime("%b %Y")
        except ValueError:
            return value
    return "Present"

env.filters["date_format"] = date_format


class Settings(BaseSettings):
    # ---- Redis ----
    REDIS_URL: str
    REDIS_STREAM_NOTIFICATION: str
    REDIS_CONSUMER_GROUP_NOTIFICATION: str

    # ---- SMTP ----
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str

    # ---- Idempotency ----
    idempotency_claim_ttl_seconds: int = 60

    SERVICE_NAME: str 

    class Config:
        env_file = ".env"
settings = Settings()
