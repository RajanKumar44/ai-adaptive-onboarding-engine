"""
Application configuration management.
Loads environment variables and provides configuration settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # ================= DATABASE =================
    DATABASE_URL: str = "sqlite:///./ai_onboarding.db"  # Default to SQLite for dev
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "ai_onboarding"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_database_url(self) -> str:
        # If DATABASE_URL is explicitly set, use it
        if self.DATABASE_URL and self.DATABASE_URL != "sqlite:///./ai_onboarding.db":
            return self.DATABASE_URL
        # Otherwise, try to use PostgreSQL if host is available
        if self.POSTGRES_HOST and self.POSTGRES_HOST != "db":
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        # Fall back to SQLite
        return "sqlite:///./ai_onboarding.db"

    # ================= APP =================
    APP_NAME: str = "AI Adaptive Onboarding Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    APP_ENV: str = "development"

    # ================= API =================
    API_PREFIX: str = "/api/v1"

    # ================= CORS =================
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:5175,"
        "http://127.0.0.1:5175"
    )

    # ================= AUTHENTICATION =================
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ================= PASSWORD REQUIREMENTS =================
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = False

    # ================= FILE =================
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "txt"]

    # ================= AI =================
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # ================= RATE LIMITING =================
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from environment variables


@lru_cache()
def get_settings() -> Settings:
    return Settings()