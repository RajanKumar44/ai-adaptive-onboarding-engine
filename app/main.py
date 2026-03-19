from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routes.analysis_routes import router as analysis_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Adaptive Onboarding Engine",
    description="Analyze resumes and job descriptions to generate personalized adaptive learning roadmaps.",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(analysis_router, prefix="/api/v1", tags=["Analysis"])


@app.get("/health", tags=["Health"])
def health_check():
    """Basic liveness probe."""
    return {"status": "ok", "service": "AI Adaptive Onboarding Engine"}


@app.get("/", tags=["Health"])
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the AI Adaptive Onboarding Engine",
        "docs": "/docs",
        "health": "/health",
    }
