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
    
    # ============================================================================
    # SECURITY CONFIGURATION
    # ============================================================================
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Configuration
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    
    # API Key Configuration
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: list = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []
    
    # Password Configuration
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # ============================================================================
    # LOGGING CONFIGURATION (PHASE 3)
    # ============================================================================
    # Environment and Application Info
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    
    # Logging Level
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "colored")  # colored (dev) or json (prod)
    
    # Log File Configuration
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "104857600"))  # 100MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "10"))
    
    # Request/Response Logging
    LOG_REQUESTS_ENABLED: bool = os.getenv("LOG_REQUESTS_ENABLED", "True").lower() == "true"
    LOG_RESPONSES_ENABLED: bool = os.getenv("LOG_RESPONSES_ENABLED", "True").lower() == "true"
    LOG_REQUEST_BODY_ENABLED: bool = os.getenv("LOG_REQUEST_BODY_ENABLED", "False").lower() == "true"
    LOG_RESPONSE_BODY_ENABLED: bool = os.getenv("LOG_RESPONSE_BODY_ENABLED", "False").lower() == "true"
    
    # ============================================================================
    # ERROR TRACKING CONFIGURATION (SENTRY)
    # ============================================================================
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")  # Set to enable Sentry
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", ENVIRONMENT)
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))  # 10% of transactions
    SENTRY_PROFILES_SAMPLE_RATE: float = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))  # 10% of profiles
    
    # ============================================================================
    # PROMETHEUS METRICS CONFIGURATION
    # ============================================================================
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "True").lower() == "true"
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "8001"))
    PROMETHEUS_METRICS_PREFIX: str = "app_"
    
    # ============================================================================
    # PERFORMANCE PROFILING CONFIGURATION
    # ============================================================================
    PROFILING_ENABLED: bool = os.getenv("PROFILING_ENABLED", "False").lower() == "true"
    PROFILING_SAMPLE_RATE: float = float(os.getenv("PROFILING_SAMPLE_RATE", "0.1"))  # 10% of requests
    SLOW_QUERY_THRESHOLD_MS: float = float(os.getenv("SLOW_QUERY_THRESHOLD_MS", "1000"))  # 1 second
    
    # ============================================================================
    # PAGINATION CONFIGURATION (PHASE 4)
    # ============================================================================
    # Default pagination settings
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    MIN_PAGE_SIZE: int = int(os.getenv("MIN_PAGE_SIZE", "1"))
    
    # Pagination presets for different entity types
    PAGINATION_SMALL_DEFAULT: int = 10  # Users, roles
    PAGINATION_SMALL_MAX: int = 50
    
    PAGINATION_MEDIUM_DEFAULT: int = 25  # Analyses, results
    PAGINATION_MEDIUM_MAX: int = 100
    
    PAGINATION_LARGE_DEFAULT: int = 50  # Logs, events
    PAGINATION_LARGE_MAX: int = 500
    
    PAGINATION_VERY_LARGE_DEFAULT: int = 100  # Audit logs
    PAGINATION_VERY_LARGE_MAX: int = 1000
    
    # ============================================================================
    # FILTERING & SORTING CONFIGURATION (PHASE 4)
    # ============================================================================
    # Supported filter operators
    ALLOWED_FILTER_OPERATORS: list = ["eq", "ne", "gt", "gte", "lt", "lte", "like", "in", "between", "is_null"]
    
    # Maximum number of filters per query
    MAX_FILTERS_PER_QUERY: int = 10
    
    # Maximum values for IN filter
    MAX_IN_FILTER_VALUES: int = 100
    
    # Fields that cannot be filtered
    FIELDS_EXCLUDE_FROM_FILTER: list = ["password_hash", "reasoning_trace"]
    
    # Default sort direction
    DEFAULT_SORT_ORDER: str = "desc"  # asc or desc
    
    # Maximum number of sort fields
    MAX_SORT_FIELDS: int = 3
    
    # ============================================================================
    # SEARCH CONFIGURATION (PHASE 4)
    # ============================================================================
    # Search modes
    SEARCH_MODES_ENABLED: list = ["simple", "phrase", "boolean", "fuzzy"]
    DEFAULT_SEARCH_MODE: str = "simple"
    
    # Search highlighting
    SEARCH_HIGHLIGHT_TAG: str = "mark"  # em, strong, mark
    SEARCH_HIGHLIGHT_ENABLED: bool = True
    
    # Full-text search settings
    MIN_SEARCH_LENGTH: int = 2
    MAX_SEARCH_LENGTH: int = 500
    
    # Search timeout (seconds)
    SEARCH_TIMEOUT_SECONDS: float = 5.0
    
    # ============================================================================
    # BULK OPERATIONS CONFIGURATION (PHASE 4)
    # ============================================================================
    # Batch size for bulk operations
    BULK_OPERATION_BATCH_SIZE: int = 100
    
    # Maximum items per bulk operation request
    BULK_OPERATION_MAX_ITEMS: int = 1000
    
    # Atomic vs partial mode settings
    BULK_OPERATION_ATOMIC_DEFAULT: bool = True
    
    # Rate limiting for bulk operations
    BULK_OPERATION_RATE_LIMIT: str = "5/minute"
    
    # ============================================================================
    # API DOCUMENTATION CONFIGURATION (PHASE 4)
    # ============================================================================
    # OpenAPI/Swagger settings
    OPENAPI_ENABLED: bool = os.getenv("OPENAPI_ENABLED", "True").lower() == "true"
    OPENAPI_URL: str = "/openapi.json"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # API documentation title and version
    API_DOCS_TITLE: str = "AI Adaptive Onboarding Engine API"
    API_DOCS_DESCRIPTION: str = "Advanced API for skill analysis and learning path generation"
    API_DOCS_VERSION: str = "1.0.0"
    
    # Enable example values in API docs
    INCLUDE_REQUEST_EXAMPLES: bool = True
    INCLUDE_RESPONSE_EXAMPLES: bool = True
    
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
