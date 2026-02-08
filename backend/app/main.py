"""
FastAPI application entry point.
Per specs/plan.md and specs/api/rest-endpoints.md
"""
from contextlib import asynccontextmanager
import logging
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from app.config import get_settings
from app.db import create_db_and_tables
from app.routes import tasks, chat, events

# Import all models so create_db_and_tables() picks them up
from app.models import Task, Conversation, Message, Reminder, AuditLog  # noqa: F401


# Structured JSON logging formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


# Configure structured logging
logging.basicConfig(level=logging.INFO)
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Request latency',
    ['method', 'endpoint']
)


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
    "https://todo-app-chatbot-roan.vercel.app/",
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
# Dapr event handlers (no prefix - Dapr expects /dapr/subscribe at root)
app.include_router(events.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"status": "healthy", "service": "hackathon-todo-api"}


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "hackathon-todo-api"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint for observability."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
