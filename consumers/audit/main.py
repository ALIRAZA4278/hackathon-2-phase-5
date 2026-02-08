"""
Audit Consumer Service

Standalone FastAPI microservice that subscribes to Dapr pub/sub topics
(todo.events, ai.events, audit.events) and persists audit log records
to the shared Neon PostgreSQL database.

Per specs/002-cloud-native-platform — Phase V cloud-native platform.
"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import FastAPI, Request
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, Field, Session, create_engine
from sqlalchemy import Column
from sqlalchemy.types import JSON

# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        json.dumps({
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "service": "audit-consumer",
            "message": "%(message)s",
        })
    )
)
logger = logging.getLogger("audit-consumer")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# ---------------------------------------------------------------------------
# Configuration (pydantic-settings)
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    """Consumer configuration loaded from environment."""
    database_url: str = ""
    service_name: str = "audit-consumer"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

# ---------------------------------------------------------------------------
# Database setup (same Neon PostgreSQL as backend)
# ---------------------------------------------------------------------------

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


class AuditLog(SQLModel, table=True):
    """
    Immutable audit log record for system operations.
    Mirrors the backend AuditLog model schema.
    """
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    action: str = Field(nullable=False)
    entity_type: str = Field(nullable=False)
    entity_id: str = Field(nullable=False)
    user_id: str = Field(index=True, nullable=False)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    details: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )


# Create tables if they do not exist (idempotent)
SQLModel.metadata.create_all(engine)

# ---------------------------------------------------------------------------
# Idempotency tracking (T065)
# In-memory set of processed idempotency keys to prevent duplicate handling.
# ---------------------------------------------------------------------------
_processed_keys: Set[str] = set()

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(title="Audit Consumer", version="1.0.0")


@app.get("/dapr/subscribe")
async def dapr_subscribe() -> List[Dict[str, str]]:
    """Return Dapr subscription list for the audit consumer."""
    return [
        {"pubsubname": "pubsub", "topic": "todo.events", "route": "/events/todo"},
        {"pubsubname": "pubsub", "topic": "ai.events", "route": "/events/ai"},
        {"pubsubname": "pubsub", "topic": "audit.events", "route": "/events/audit"},
    ]


def _extract_event_data(body: dict) -> dict:
    """Extract event data from CloudEvent envelope or raw payload."""
    return body.get("data", body)


def _is_duplicate(idempotency_key: str) -> bool:
    """Check if an event has already been processed."""
    if idempotency_key in _processed_keys:
        logger.info("Duplicate event skipped: key=%s", idempotency_key)
        return True
    return False


def _mark_processed(idempotency_key: str) -> None:
    """Record that an event has been processed."""
    _processed_keys.add(idempotency_key)


def _persist_audit_record(event_data: dict) -> None:
    """Insert an audit log record into the database."""
    event_type = event_data.get("event_type", "unknown")
    entity_id = event_data.get("entity_id", "unknown")
    user_id = event_data.get("user_id", "unknown")
    payload = event_data.get("payload", {})

    # Derive entity_type from event_type (e.g., "task_created" -> "task")
    entity_type = event_type.split("_")[0] if "_" in event_type else "unknown"

    record = AuditLog(
        action=event_type,
        entity_type=entity_type,
        entity_id=str(entity_id),
        user_id=user_id,
        timestamp=datetime.now(timezone.utc),
        details=payload if payload else None,
    )

    try:
        with Session(engine) as session:
            session.add(record)
            session.commit()
            logger.info(
                "Audit record persisted: action=%s entity=%s user=%s",
                event_type, entity_id, user_id,
            )
    except Exception as exc:
        logger.error("Failed to persist audit record: %s", exc)


@app.post("/events/todo")
async def handle_todo_event(request: Request) -> Dict[str, str]:
    """Handle todo.events for audit logging."""
    try:
        body = await request.json()
        event_data = _extract_event_data(body)
        idempotency_key = event_data.get("idempotency_key", "")

        if idempotency_key and _is_duplicate(idempotency_key):
            return {"status": "SUCCESS"}

        logger.info(
            "Audit todo event: type=%s entity=%s user=%s",
            event_data.get("event_type"),
            event_data.get("entity_id"),
            event_data.get("user_id"),
        )
        _persist_audit_record(event_data)

        if idempotency_key:
            _mark_processed(idempotency_key)
    except Exception as exc:
        logger.error("Error handling todo event: %s", exc)

    return {"status": "SUCCESS"}


@app.post("/events/ai")
async def handle_ai_event(request: Request) -> Dict[str, str]:
    """Handle ai.events for audit logging."""
    try:
        body = await request.json()
        event_data = _extract_event_data(body)
        idempotency_key = event_data.get("idempotency_key", "")

        if idempotency_key and _is_duplicate(idempotency_key):
            return {"status": "SUCCESS"}

        logger.info(
            "Audit AI event: type=%s entity=%s user=%s",
            event_data.get("event_type"),
            event_data.get("entity_id"),
            event_data.get("user_id"),
        )
        _persist_audit_record(event_data)

        if idempotency_key:
            _mark_processed(idempotency_key)
    except Exception as exc:
        logger.error("Error handling AI event: %s", exc)

    return {"status": "SUCCESS"}


@app.post("/events/audit")
async def handle_audit_event(request: Request) -> Dict[str, str]:
    """Handle audit.events for audit logging."""
    try:
        body = await request.json()
        event_data = _extract_event_data(body)
        idempotency_key = event_data.get("idempotency_key", "")

        if idempotency_key and _is_duplicate(idempotency_key):
            return {"status": "SUCCESS"}

        logger.info(
            "Audit event: type=%s entity=%s user=%s",
            event_data.get("event_type"),
            event_data.get("entity_id"),
            event_data.get("user_id"),
        )
        _persist_audit_record(event_data)

        if idempotency_key:
            _mark_processed(idempotency_key)
    except Exception as exc:
        logger.error("Error handling audit event: %s", exc)

    return {"status": "SUCCESS"}


# ---------------------------------------------------------------------------
# Health & Metrics endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": settings.service_name}


@app.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """Prometheus metrics endpoint (placeholder)."""
    return {
        "service": settings.service_name,
        "processed_events": len(_processed_keys),
        "status": "ok",
    }
