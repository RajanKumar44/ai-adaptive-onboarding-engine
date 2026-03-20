"""
Sentry Integration Module

Provides error tracking and monitoring integration with Sentry:
- Automatic exception tracking
- Performance monitoring
- Release tracking
- Environment tagging
- Breadcrumb tracking
- Session management
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from typing import Optional
import logging
from .config import settings


class SentryManager:
    """Manages Sentry SDK initialization and configuration"""
    
    _initialized = False
    
    @classmethod
    def initialize(cls, dsn: Optional[str] = None) -> None:
        """Initialize Sentry SDK"""
        if cls._initialized:
            return
        
        # Use provided DSN or from settings
        sentry_dsn = dsn or settings.SENTRY_DSN
        
        if not sentry_dsn:
            # Sentry disabled if no DSN
            return
        
        try:
            sentry_sdk.init(
                dsn=sentry_dsn,
                
                # Environment and release
                environment=settings.ENVIRONMENT,
                release=settings.APP_VERSION,
                
                # Performance monitoring
                traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
                profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
                
                # Integrations
                integrations=[
                    FastApiIntegration(transaction_style="endpoint"),
                    SqlalchemyIntegration(),
                    LoggingIntegration(
                        level=logging.INFO,  # Capture info and above as breadcrumbs
                        event_level=logging.ERROR  # Send errors as events
                    ),
                    ThreadingIntegration(),
                    HttpxIntegration(),
                ],
                
                # Error tracking
                max_breadcrumbs=100,
                attach_stacktrace=True,
                send_default_pii=False,  # Don't send PII by default
                
                # Before send hook for filtering
                before_send=cls._before_send,
                before_send_transaction=cls._before_send_transaction,
            )
            
            # Set user context (will be updated per request)
            sentry_sdk.set_context(
                "service",
                {
                    "name": "ai-adaptive-onboarding-engine",
                    "version": settings.APP_VERSION
                }
            )
            
            cls._initialized = True
            logging.getLogger(__name__).info("Sentry initialized successfully")
            
        except Exception as e:
            logging.getLogger(__name__).error(
                f"Failed to initialize Sentry: {str(e)}"
            )
    
    @staticmethod
    def _before_send(event: dict, hint: dict) -> Optional[dict]:
        """Filter events before sending to Sentry"""
        
        # Don't send 404 errors
        if event.get("request"):
            status_code = event["request"].get("status_code")
            if status_code == 404:
                return None
        
        # Don't send 429 (rate limit) errors
        if event.get("request"):
            status_code = event["request"].get("status_code")
            if status_code == 429:
                return None
        
        # Filter by exception type
        if "exception" in event:
            exc_type = event["exception"]["values"][0]["type"]
            
            # Ignore certain exceptions
            ignored_exceptions = [
                "ValidationError",
                "HTTPException",
                "RequestValidationError"
            ]
            
            if exc_type in ignored_exceptions:
                return None
        
        return event
    
    @staticmethod
    def _before_send_transaction(event: dict, hint: dict) -> Optional[dict]:
        """Filter transactions before sending to Sentry"""
        
        # Don't send health check transactions
        if event.get("transaction"):
            if "/health" in event["transaction"]:
                return None
        
        # Filter out high latency thresholds (optional)
        if event.get("transaction") and event.get("measurements"):
            duration = event["measurements"].get("duration", {}).get("value", 0)
            
            # Sample slow transactions more often
            if duration > 5000:  # More than 5 seconds
                # Always send slow transactions
                pass
        
        return event
    
    @classmethod
    def set_user_context(cls, user_id: str, email: str = None, role: str = None):
        """Set user context for error tracking"""
        if not cls._initialized:
            return
        
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "ip_address": "{{auto}}"
        })
        
        if role:
            sentry_sdk.set_context("user", {"role": role})
    
    @classmethod
    def clear_user_context(cls):
        """Clear user context"""
        if not cls._initialized:
            return
        
        sentry_sdk.set_user(None)
    
    @classmethod
    def capture_message(cls, message: str, level: str = "info", extra: dict = None):
        """Manually capture a message"""
        if not cls._initialized:
            return
        
        sentry_sdk.capture_message(message, level=level)
        
        if extra:
            sentry_sdk.set_context("extra", extra)
    
    @classmethod
    def capture_exception(cls, exception: Exception, extra: dict = None):
        """Manually capture an exception"""
        if not cls._initialized:
            return
        
        sentry_sdk.capture_exception(exception)
        
        if extra:
            sentry_sdk.set_context("extra", extra)
    
    @classmethod
    def add_breadcrumb(cls, message: str, category: str = "default", 
                       level: str = "info", data: dict = None):
        """Add a breadcrumb for tracking user actions"""
        if not cls._initialized:
            return
        
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )
    
    @classmethod
    def start_transaction(cls, name: str, op: str = "http.server"):
        """Start a transaction for performance monitoring"""
        if not cls._initialized:
            return None
        
        return sentry_sdk.start_transaction(
            name=name,
            op=op,
            tracing=True
        )
    
    @classmethod
    def set_tag(cls, key: str, value: str):
        """Set a tag for filtering in Sentry"""
        if not cls._initialized:
            return
        
        sentry_sdk.set_tag(key, value)
    
    @classmethod
    def set_tags(cls, tags: dict):
        """Set multiple tags"""
        if not cls._initialized:
            return
        
        for key, value in tags.items():
            sentry_sdk.set_tag(key, value)


def setup_sentry_middleware(app):
    """Setup Sentry middleware for FastAPI app"""
    
    from starlette.middleware.errors import ServerErrorMiddleware
    
    # Sentry middleware is auto-added via integrations
    # This function is for any additional setup needed
    
    @app.middleware("http")
    async def sentry_context_middleware(request, call_next):
        """Set Sentry context for each request"""
        
        # Set request context
        sentry_sdk.set_context(
            "request",
            {
                "method": request.method,
                "path": request.url.path,
                "headers": dict(request.headers)
            }
        )
        
        # Set user context if authenticated
        try:
            if hasattr(request.state, "user"):
                SentryManager.set_user_context(
                    user_id=str(request.state.user.id),
                    email=request.state.user.email,
                    role=request.state.user.role
                )
        except Exception:
            pass
        
        response = await call_next(request)
        return response


# Initialize Sentry on module import
SentryManager.initialize()
