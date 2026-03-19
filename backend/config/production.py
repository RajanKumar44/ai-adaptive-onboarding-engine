"""
Extended configuration with additional settings for production deployment.
"""

from app.core.config import get_settings as get_base_settings

settings = get_base_settings()

# Extended Production Settings
PRODUCTION_CONFIG = {
    # Security
    "SECRET_KEY": "your-secret-key-here",  # MUST be set in production
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    
    # CORS
    "ALLOWED_ORIGINS": [
        "http://localhost:3000",
        "https://yourdomain.com",
    ],
    
    # API Rate Limiting
    "RATE_LIMIT": {
        "enabled": True,
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
    },
    
    # Logging
    "LOGGING": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/app.log",
    },
    
    # Cache
    "CACHE": {
        "enabled": True,
        "type": "redis",  # or memcached
        "ttl": 3600,
    },
    
    # Email
    "EMAIL": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
    },
    
    # Monitoring
    "MONITORING": {
        "enabled": True,
        "prometheus": True,
        "sentry": False,
    },
    
    # Database
    "DATABASE": {
        "pool_size": 20,
        "max_overflow": 40,
        "pool_recycle": 3600,
    },
}

# Feature Flags
FEATURE_FLAGS = {
    "llm_extraction": False,  # Enable LLM-based skill extraction
    "email_notifications": False,  # Enable email notifications
    "advanced_analytics": False,  # Advanced analytics dashboard
    "user_authentication": False,  # JWT authentication
}
