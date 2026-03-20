"""
FastAPI main application entry point.
Initializes the application with all dependencies and routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.config import get_settings
from app.core.database import init_db
from app.routes.analysis_routes import router as analysis_router
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.metrics_routes import router as metrics_router
from app.middleware.rate_limiting import limiter

# Import logging and monitoring modules (Phase 3)
import logging
from app.core.logging_config import LoggerManager, logger
from app.core.sentry_config import SentryManager, setup_sentry_middleware
from app.middleware.logging_middleware import (
    StructuredLoggingMiddleware,
    RequestIDMiddleware,
    PerformanceMetricsMiddleware,
    ErrorLoggingMiddleware
)
from app.middleware.prometheus_middleware import (
    PrometheusMetricsMiddleware,
    MetricsRecorderMiddleware,
    DatabaseMetricsMiddleware
)

# Initialize settings
settings = get_settings()

# Initialize logging system
LoggerManager.initialize()

# Initialize Sentry error tracking
SentryManager.initialize()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Complete backend system for AI Adaptive Onboarding Engine with JWT Authentication, Logging, and Monitoring",
    version=settings.APP_VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# ============================================================================
# MIDDLEWARE STACK (Order matters!)
# ============================================================================

# 1. Error logging middleware (outermost to catch all errors)
app.add_middleware(ErrorLoggingMiddleware)

# 2. Request ID middleware (generates request ID for tracing)
app.add_middleware(RequestIDMiddleware)

# 3. Structured logging middleware (logs all requests/responses)
app.add_middleware(
    StructuredLoggingMiddleware,
    skip_paths=[
        "/health", "/api/v1/health",
        "/metrics", "/api/v1/metrics",
        "/docs", "/openapi.json", "/redoc"
    ]
)

# 4. Performance metrics middleware (tracks endpoint performance)
app.add_middleware(PerformanceMetricsMiddleware)

# 5. Prometheus metrics middleware (collects Prometheus metrics)
app.add_middleware(PrometheusMetricsMiddleware)

# 6. Metrics recorder middleware (records specific application metrics)
app.add_middleware(MetricsRecorderMiddleware)

# 7. Rate limiter exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 8. CORS middleware (standard configuration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 9. Trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In production, specify allowed hosts
)

# Setup Sentry middleware for error tracking
setup_sentry_middleware(app)


# ============================================================================
# STARTUP AND SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup.
    - Database connection
    - Logging system
    - Monitoring tools
    """
    try:
        # Initialize database
        init_db()
        logger.info("✓ Database initialized successfully")
        
        # Initialize Prometheus metrics
        logger.info("✓ Prometheus metrics initialized")
        
        # Initialize Sentry if configured
        if settings.SENTRY_DSN:
            logger.info("✓ Sentry error tracking enabled")
        else:
            logger.info("⚠ Sentry not configured (DSN not set)")
        
        # Log startup information
        logger.info(
            "Application startup complete",
            extra={
                "environment": settings.ENVIRONMENT,
                "version": settings.APP_VERSION,
                "logging_enabled": True,
                "monitoring_enabled": True
            }
        )
        
    except Exception as e:
        logger.error(f"✗ Startup initialization failed: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown.
    """
    try:
        logger.info("Application shutting down")
        # Additional cleanup can be added here
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


# ============================================================================
# ROUTER INCLUSION
# ============================================================================

# Include routers
app.include_router(auth_router)       # Auth routes (login, register, etc.)
app.include_router(analysis_router)   # Analysis routes
app.include_router(admin_router)      # Admin routes (user management)
app.include_router(metrics_router)    # Metrics and monitoring endpoints


# ============================================================================
# HEALTH CHECK & ROOT ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Quick health check endpoint (lightweight, no metrics recorded)"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/v1/health")
async def api_health_check():
    """API v1 health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "service": settings.APP_NAME
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root API endpoint with service information.
    
    Returns:
        Service metadata
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/v1/docs",
        "monitoring": {
            "prometheus": "/api/v1/metrics/prometheus",
            "health": "/api/v1/health",
            "status": "/api/v1/metrics/status",
            "performance": "/api/v1/metrics/performance",
            "logs": "/api/v1/metrics/logs-info",
            "sentry": "/api/v1/metrics/sentry-info"
        },
        "endpoints": {
            "auth_register": "POST /api/v1/auth/register",
            "auth_login": "POST /api/v1/auth/login",
            "auth_refresh": "POST /api/v1/auth/refresh",
            "auth_logout": "POST /api/v1/auth/logout",
            "auth_me": "GET /api/v1/auth/me",
            "analyze": "POST /api/v1/analyze",
            "get_analysis": "GET /api/v1/analysis/{id}",
            "user_analyses": "GET /api/v1/users/{user_id}/analyses",
            "admin_users": "GET /api/v1/admin/users",
        }
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    
    Logs error and captures in Sentry if configured.
    
    Args:
        request: Request object
        exc: Exception object
        
    Returns:
        Error response
    """
    # Log the exception
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True
    )
    
    # Capture in Sentry if configured
    try:
        if settings.SENTRY_DSN:
            SentryManager.capture_exception(exc)
    except:
        pass
    
    return {
        "error": "Internal Server Error",
        "detail": str(exc) if settings.DEBUG else "An error occurred",
        "status_code": 500,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
