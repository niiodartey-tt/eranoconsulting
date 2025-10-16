import os
import secrets
from typing import Optional, Any
from pydantic import PostgresDsn, EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Eranos Consulting API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: list[str] | str = "*"

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_PRE_PING: bool = True

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_UPLOAD_TYPES: set[str] = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    UPLOAD_DIR: str = "backend/uploads"

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Redis (for caching/sessions)
    REDIS_URL: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # ✅ Pydantic v2 compatible field validators
    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "change_me_in_production":
            raise ValueError("You must set a secure SECRET_KEY")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [i.strip() for i in v.split(",")]
        return v

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if "sqlite" in str(v):
            raise ValueError("SQLite is not recommended for production")
        return v

    # ✅ Replaces `class Config` in Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
