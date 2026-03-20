"""
Rate limiting middleware using slowapi.
Protects endpoints from abuse and DDoS attacks.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import get_settings

settings = get_settings()

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

# Define reusable rate limit decorators
class RateLimits:
    """Rate limit definitions for different endpoint types."""
    
    # Authentication endpoints (strict)
    LOGIN = "5/minute"          # 5 login attempts per minute
    REGISTER = "3/minute"       # 3 register attempts per minute
    REFRESH_TOKEN = "10/minute" # 10 token refreshes per minute
    
    # Main endpoints (moderate)
    ANALYZE = "10/minute"       # 10 analyses per minute
    HEALTH = "60/minute"        # 60 health checks per minute
    
    # General API (relaxed)
    GENERAL = f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute"
    HOURLY = f"{settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour"
