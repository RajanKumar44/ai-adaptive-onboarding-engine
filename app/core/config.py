import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/onboarding_db"
    DEBUG: bool = False
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10485760  # 10 MB in bytes

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
