"""
Application configuration loaded from environment variables.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = ""

    # JWT Secret (must match frontend BETTER_AUTH_SECRET)
    better_auth_secret: str = ""

    # CORS
    frontend_url: str = "https://todo-app-chatbot-roan.vercel.app"

    # JWT Configuration
    jwt_algorithm: str = "HS256"

    # AI Chatbot Configuration (Phase III)
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
