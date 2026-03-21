"""
FastAPI main application entry point.
Initializes the application with all dependencies and routes.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import init_db
from app.routes.analysis_routes import router as analysis_router
from app.routes.auth_routes import router as auth_router
from app.routes.admin_routes import router as admin_router
from app.routes.bulk_routes import router as bulk_router
from app.routes.llm_routes import router as llm_router
from app.routes.metrics_routes import router as metrics_router

# Import all models so they're registered with SQLAlchemy Base
from app.models import User, Analysis, AuditLog

# Load settings
settings = get_settings()


# ================= LIFESPAN (MODERN STARTUP) =================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup & shutdown events.
    """
    try:
        print("🔧 Initializing database tables...")
        print(f"Models imported: User={User}, Analysis={Analysis}, AuditLog={AuditLog}")
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

    yield

    print("🛑 Application shutdown")


# ================= CREATE APP =================
app = FastAPI(
    title=settings.APP_NAME,
    description="Complete backend system for AI Adaptive Onboarding Engine",
    version=settings.APP_VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)


# ================= MIDDLEWARE =================

# CORS (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ change in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # ⚠️ restrict in production
)


# ================= ROUTES =================
app.include_router(analysis_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(bulk_router)
app.include_router(llm_router)
app.include_router(metrics_router)


# ================= ROOT =================
@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/v1/docs",
    }


# ================= GLOBAL ERROR HANDLER =================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "Something went wrong",
        },
    )


# ================= RUN =================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )