"""
Application configuration management.
Loads environment variables and provides configuration settings.
"""

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Database Configuration
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_onboarding")
    
    # SQLAlchemy Database URL
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Application Configuration
    APP_NAME: str = "AI Adaptive Onboarding Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API Configuration
    API_PREFIX: str = "/api/v1"
    
    # File Upload Configuration
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ["pdf", "txt"]
    
    # AI Configuration (LLM placeholder)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # Can be swapped later
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Returns the same instance for all requests.
    """
    return Settings()
