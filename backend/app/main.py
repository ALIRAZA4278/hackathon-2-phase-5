"""
FastAPI application entry point.
Per specs/plan.md and specs/api/rest-endpoints.md
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.db import create_db_and_tables
from app.routes import tasks, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Creates database tables on startup.
    """
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (nothing to clean up)


# Create FastAPI application
app = FastAPI(
    title="Hackathon Todo API",
    description="Phase II - Full-Stack Todo Application Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
# Allow multiple origins for flexibility (localhost + production)
allowed_origins = [
    settings.frontend_url,
    "http://localhost:3000",
    "https://localhost:3000",
]
# Filter out empty strings and duplicates
allowed_origins = list(set(filter(None, allowed_origins)))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers
app.include_router(tasks.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "hackathon-todo-api"}
