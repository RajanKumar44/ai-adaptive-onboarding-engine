"""
FastAPI main application entry point.
Initializes the application with all dependencies and routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import get_settings
from app.core.database import init_db
from app.routes.analysis_routes import router as analysis_router

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Complete backend system for AI Adaptive Onboarding Engine",
    version=settings.APP_VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(analysis_router)


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
            "health": "/api/v1/health",
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
