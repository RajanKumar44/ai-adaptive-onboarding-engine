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
from app.middleware.rate_limiting import limiter

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Complete backend system for AI Adaptive Onboarding Engine with JWT Authentication",
    version=settings.APP_VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware with configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In production, specify allowed hosts
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """
    Initialize database and create tables on application startup.
    """
    try:
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {str(e)}")


# Include routers
app.include_router(auth_router)      # Auth routes (login, register, etc.)
app.include_router(analysis_router)   # Analysis routes


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
        "endpoints": {
            "auth_register": "POST /api/v1/auth/register",
            "auth_login": "POST /api/v1/auth/login",
            "auth_refresh": "POST /api/v1/auth/refresh",
            "auth_logout": "POST /api/v1/auth/logout",
            "auth_me": "GET /api/v1/auth/me",
            "health": "GET /api/v1/health",
            "create_user": "POST /api/v1/users",
            "analyze": "POST /api/v1/analyze",
            "get_analysis": "GET /api/v1/analysis/{id}",
            "user_analyses": "GET /api/v1/users/{user_id}/analyses",
        }
    }


# Error handler for generic exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    
    Args:
        request: Request object
        exc: Exception object
        
    Returns:
        Error response
    """
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
