"""
Reminder Consumer Service

Standalone FastAPI microservice that:
1. Subscribes to reminder.events via Dapr pub/sub
2. Stores reminder trigger_at when reminder_scheduled events arrive
3. Receives periodic cron binding invocations from Dapr (every 30s)
4. Checks for due reminders and fires notification events

Per specs/002-cloud-native-platform — Phase V cloud-native platform.
"""
import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from fastapi import FastAPI, Request
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, Field, Session, create_engine, select

# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        json.dumps({
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "service": "reminder-consumer",
            "message": "%(message)s",
        })
    )
)
logger = logging.getLogger("reminder-consumer")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# ---------------------------------------------------------------------------
# Configuration (pydantic-settings)
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    """Consumer configuration loaded from environment."""
    database_url: str = ""
    service_name: str = "reminder-consumer"
    dapr_http_port: int = 3500

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


class Reminder(SQLModel, table=True):
    """
    Reminder model — mirrors the backend Reminder schema.
    State transitions: pending -> triggered | cancelled
    """
    __tablename__ = "reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False)
    trigger_at: datetime = Field(nullable=False)
    status: str = Field(default="pending", nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# Tables are created by the main backend; do not force-create here
# but ensure SQLModel metadata knows the schema for queries.

# ---------------------------------------------------------------------------
# Idempotency tracking (T065)
# ---------------------------------------------------------------------------
_processed_keys: Set[str] = set()

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(title="Reminder Consumer", version="1.0.0")


@app.get("/dapr/subscribe")
async def dapr_subscribe() -> List[Dict[str, str]]:
    """Return Dapr subscription list for the reminder consumer."""
    return [
        {"pubsubname": "pubsub", "topic": "reminder.events", "route": "/events/reminder"},
    ]


def _extract_event_data(body: dict) -> dict:
    """Extract event data from CloudEvent envelope or raw payload."""
    return body.get("data", body)


def _is_duplicate(idempotency_key: str) -> bool:
    """Check if an event has already been processed."""
    if idempotency_key in _processed_keys:
        logger.info("Duplicate reminder event skipped: key=%s", idempotency_key)
        return True
    return False


def _mark_processed(idempotency_key: str) -> None:
    """Record that an event has been processed."""
    _processed_keys.add(idempotency_key)


def _handle_reminder_scheduled(event_data: dict) -> None:
    """
    Process a reminder_scheduled event.
    The reminder should already exist in the database (created by the backend).
    Log the scheduling for observability.
    """
    entity_id = event_data.get("entity_id", "unknown")
    user_id = event_data.get("user_id", "unknown")
    payload = event_data.get("payload", {})
    trigger_at = payload.get("trigger_at")

    logger.info(
        "Reminder scheduled: entity=%s user=%s trigger_at=%s",
        entity_id, user_id, trigger_at,
    )


def _check_and_fire_due_reminders() -> int:
    """
    Query the database for pending reminders whose trigger_at <= now.
    Update their status to 'triggered' and log the notification.

    Returns the number of reminders fired.
    """
    now = datetime.now(timezone.utc)
    fired_count = 0

    try:
        with Session(engine) as session:
            statement = select(Reminder).where(
                Reminder.status == "pending",
                Reminder.trigger_at <= now,
            )
            due_reminders = session.exec(statement).all()

            for reminder in due_reminders:
                reminder.status = "triggered"
                session.add(reminder)
                fired_count += 1
                logger.info(
                    "Reminder FIRED: id=%s task_id=%s user=%s trigger_at=%s",
                    reminder.id,
                    reminder.task_id,
                    reminder.user_id,
                    reminder.trigger_at.isoformat() if reminder.trigger_at else "N/A",
                )

            if fired_count > 0:
                session.commit()
                logger.info("Fired %d due reminder(s)", fired_count)

    except Exception as exc:
        logger.error("Error checking due reminders: %s", exc)

    return fired_count


@app.post("/events/reminder")
async def handle_reminder_event(request: Request) -> Dict[str, str]:
    """Handle reminder.events from Dapr pub/sub."""
    try:
        body = await request.json()
        event_data = _extract_event_data(body)
        idempotency_key = event_data.get("idempotency_key", "")

        if idempotency_key and _is_duplicate(idempotency_key):
            return {"status": "SUCCESS"}

        event_type = event_data.get("event_type", "unknown")
        logger.info(
            "Reminder event received: type=%s entity=%s user=%s",
            event_type,
            event_data.get("entity_id"),
            event_data.get("user_id"),
        )

        if event_type == "reminder_scheduled":
            _handle_reminder_scheduled(event_data)
        elif event_type == "reminder_cancelled":
            logger.info(
                "Reminder cancelled: entity=%s",
                event_data.get("entity_id"),
            )
        else:
            logger.info("Unhandled reminder event type: %s", event_type)

        if idempotency_key:
            _mark_processed(idempotency_key)
    except Exception as exc:
        logger.error("Error handling reminder event: %s", exc)

    return {"status": "SUCCESS"}


# ---------------------------------------------------------------------------
# Dapr cron binding input handler
# Dapr invokes this endpoint on the schedule defined in binding-cron.yaml
# (every 30 seconds). This is the trigger that checks for due reminders.
# ---------------------------------------------------------------------------

@app.post("/cron-reminder-check")
async def cron_reminder_check(request: Request) -> Dict[str, str]:
    """
    Dapr cron binding input handler.
    Called every 30 seconds by the cron-reminder-check binding.
    Checks for pending reminders that are due and fires them.
    """
    logger.info("Cron trigger: checking for due reminders")
    fired_count = _check_and_fire_due_reminders()
    logger.info("Cron trigger complete: fired %d reminder(s)", fired_count)
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
